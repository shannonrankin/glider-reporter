import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {test} from 'node:test';
import h5wasm from 'h5wasm/node';
import * as netcdfjs from 'netcdfjs';

// Execute the OJS definitions used by the page, substituting only the browser CDN imports.
const page = readFileSync(new URL('../data_intake.qmd', import.meta.url), 'utf8');
const source = page.split('data_intake_snake_case = ')[1]
  ?.split('\n```')[0];
assert.ok(source, 'The data intake OJS parser cell must be present');
const definitions = `data_intake_snake_case = ${source}`
  .replace(/await import\(\s*"https:\/\/cdn\.jsdelivr\.net\/npm\/h5wasm@0\.10\.3\/dist\/esm\/hdf5_hl\.js"\s*\)/g,
    'await Promise.resolve(hdf5Module)')
  .replace(/await import\(\s*"https:\/\/cdn\.jsdelivr\.net\/npm\/netcdfjs@4\.0\.0\/\+esm"\s*\)/g,
    'await Promise.resolve(netcdfModule)');
assert.ok(!definitions.includes('cdn.jsdelivr.net'), 'Both reader imports must use the local test packages');
const {
  flattenValues, flattenVariables, parseHdf5, parseNetcdf, parseCsv, parseUpload
} = new Function('hdf5Module', 'netcdfModule', `
  ${definitions}
  return {
    flattenValues: data_intake_flatten_values,
    flattenVariables: data_intake_flatten_variables,
    parseHdf5: data_intake_parse_hdf5,
    parseNetcdf: data_intake_parse_netcdf,
    parseCsv: data_intake_parse_csv,
    parseUpload: data_intake_parse_upload
  };
`)({default: h5wasm}, netcdfjs);

function variable(name, shape, values, dimensions) {
  return {name, shape, values, dimensions};
}

function fixture(name) {
  const bytes = readFileSync(new URL(`./fixtures/${name}`, import.meta.url));
  return {
    name,
    size: bytes.length,
    async arrayBuffer() {
      return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
    }
  };
}

test('recursive flattening preserves nested, scalar, and typed numeric values', () => {
  assert.deepEqual(flattenValues([1, [2, [3, 4]], 5]), [1, 2, 3, 4, 5]);
  assert.deepEqual(flattenValues(42), [42]);
  for (const TypedArray of [Float32Array, Float64Array]) {
    const result = flattenValues(new TypedArray([1.5, 2.5, 3.5]));
    assert.ok(Array.isArray(result));
    assert.deepEqual(result, [1.5, 2.5, 3.5]);
  }
});

test('scalar, 1-D, and 2-D variables produce complete rows', () => {
  const extracted = flattenVariables([
    variable('temperature', [2, 3], [[10, 11, 12], [20, 21, 22]], ['time', 'depth']),
    variable('time', [2], new Float32Array([0, 1]), ['time']),
    variable('latitude', [2], new Float32Array([40, 41]), ['time']),
    variable('longitude', [2], new Float64Array([-70, -71]), ['time']),
    variable('depth', [3], [0, 5, 10], ['depth']),
    variable('station', [], 42, [])
  ]);
  assert.deepEqual(extracted.warnings, []);
  assert.deepEqual(extracted.rows.map(({temperature}) => temperature), [10, 11, 12, 20, 21, 22]);
  assert.deepEqual(extracted.rows.map(({time}) => time), [0, 0, 0, 1, 1, 1]);
  assert.deepEqual(extracted.rows.map(({latitude}) => latitude), [40, 40, 40, 41, 41, 41]);
  assert.deepEqual(extracted.rows.map(({longitude}) => longitude), [-70, -70, -70, -71, -71, -71]);
  assert.deepEqual(extracted.rows.map(({depth}) => depth), [0, 5, 10, 0, 5, 10]);
  assert.deepEqual(extracted.rows.map(({station}) => station), Array(6).fill(42));
});

test('shape mismatches and 3-D grids are skipped, never silently truncated or reinterpreted', () => {
  const extracted = flattenVariables([
    variable('time', [4], new Float32Array([0, 1, 2, 3]), ['time']),
    variable('bad_shape', [2, 3], [1, 2, 3, 4, 5], ['time', 'depth']),
    variable('grid', [2, 3, 4], Array(24).fill(99), ['time', 'depth', 'other'])
  ]);
  assert.equal(extracted.rows.length, 4);
  assert.deepEqual(extracted.rows.map(({time}) => time), [0, 1, 2, 3]);
  assert.ok(extracted.rows.every((row) => !('bad_shape' in row) && !('grid' in row)));
  assert.match(extracted.warnings.join(' '), /bad_shape.*stored shape does not match its values/);
  assert.match(extracted.warnings.join(' '), /grid.*3-dimensional grid cannot be flattened safely/);
});

test('named axes disambiguate a square grid; an unlabeled axis is rejected', () => {
  const extracted = flattenVariables([
    variable('temperature', [2, 2], [10, 11, 20, 21], ['time', 'depth']),
    variable('latitude', [2], [40, 41], ['time']),
    variable('depth', [2], [0, 5], ['depth']),
    variable('unknown', [2], [8, 9])
  ]);
  assert.deepEqual(extracted.rows.map(({latitude, depth}) => [latitude, depth]),
    [[40, 0], [40, 5], [41, 0], [41, 5]]);
  assert.ok(extracted.rows.every((row) => !('unknown' in row)));
  assert.match(extracted.warnings.join(' '), /unknown.*unlabeled axis is ambiguous/);
});

test('the HDF5 fixture passes through h5wasm and the actual upload parser', async () => {
  const result = await parseUpload(fixture('data_intake_profile.h5'));
  assert.equal(result.format, 'HDF5 Container');
  assert.deepEqual(result.warnings, []);
  assert.deepEqual(result.rows.map((row) => row.temperature), [10, 11, 12, 20, 21, 22]);
  assert.deepEqual(result.rows.map((row) => [row.latitude, row.depth]),
    [[40, 0], [40, 5], [40, 10], [41, 0], [41, 5], [41, 10]]);
});

test('the NetCDF fixture retains dimensions, converts char values, and aligns coordinates', async () => {
  const result = await parseUpload(fixture('data_intake_profile.nc'));
  assert.equal(result.format, 'NetCDF (OG1.0)');
  assert.deepEqual(result.warnings, []);
  assert.deepEqual(result.rows.map((row) => row.temperature), [10, 11, 12, 20, 21, 22]);
  assert.deepEqual(result.rows.map((row) => [row.time, row.latitude, row.longitude, row.depth, row.label]),
    [[0, 40, -70, 0, 'A'], [0, 40, -70, 5, 'A'], [0, 40, -70, 10, 'A'],
      [1, 41, -71, 0, 'B'], [1, 41, -71, 5, 'B'], [1, 41, -71, 10, 'B']]);
});

test('existing CSV parsing and upload safety limit remain unchanged', async () => {
  assert.deepEqual({...parseCsv('Latitude,Time\n40,2024-01-01\n')[0]},
    {latitude: '40', time: '2024-01-01'});
  await assert.rejects(parseUpload({name: 'large.nc', size: 250 * 1024 * 1024 + 1}),
    /Files larger than 250 MB/);
});
