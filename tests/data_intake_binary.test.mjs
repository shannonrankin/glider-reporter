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

function cfFixture({units, calendar, noCalendar, times} = {}) {
  const bytes = Buffer.from(readFileSync(new URL('./fixtures/data_intake_cf_time.nc', import.meta.url)));
  const replaceAttribute = (original, replacement) => {
    assert.ok(replacement.length <= original.length);
    const position = bytes.indexOf(original);
    assert.ok(position >= 0, `${original} must occur in the fixture`);
    bytes.write(replacement.padEnd(original.length), position, 'ascii');
  };
  if (units) replaceAttribute('seconds since 1970-01-01T00:00:00Z', units);
  if (calendar) replaceAttribute('gregorian', calendar);
  if (noCalendar) replaceAttribute('calendar', 'othercal');
  if (times) {
    const reader = new netcdfjs.NetCDFReader(bytes);
    const offset = reader.variables.find((variable) => variable.name === 'time').offset;
    times.forEach((value, index) => bytes.writeDoubleBE(value, offset + index * 8));
  }
  return {
    name: 'data_intake_cf_time.nc',
    size: bytes.length,
    async arrayBuffer() {
      return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
    }
  };
}

function validate(rows, mapping) {
  const code = page.split('data_intake_canonical_time = ')[1]?.split('\n```')[0];
  assert.ok(code, 'The OG1.0 validation cell must be present');
  const validation = `data_intake_canonical_time = ${code}`
    .replace('data_intake_validation = {', 'return (() => {')
    .replace(/\}\s*$/, '})()');
  return new Function('data_intake_loaded', 'data_intake_mapping', validation)(
    {rows}, mapping
  );
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
  assert.match(result.warnings.join(' '), /time variable.*units.*missing or invalid/);
  assert.deepEqual(result.rows.map((row) => row.temperature), [10, 11, 12, 20, 21, 22]);
  assert.deepEqual(result.rows.map((row) => [row.time, row.latitude, row.longitude, row.depth, row.label]),
    [[0, 40, -70, 0, 'A'], [0, 40, -70, 5, 'A'], [0, 40, -70, 10, 'A'],
      [1, 41, -71, 0, 'B'], [1, 41, -71, 5, 'B'], [1, 41, -71, 10, 'B']]);
  const validation = validate(result.rows, {
    time: 'time', latitude: 'latitude', longitude: 'longitude', depth: 'depth'
  });
  assert.deepEqual(validation.missingRequired, []);
  assert.deepEqual(validation.standardizedRows.map((row) => [row.latitude, row.longitude, row.depth]),
    result.rows.map((row) => [row.latitude, row.longitude, row.depth]));
  assert.deepEqual(validation.issues, ['6 row(s) contain blank or malformed timestamps.']);
});

test('CF NetCDF numeric time decodes through upload, alignment, and OG1.0 validation', async () => {
  const result = await parseUpload(fixture('data_intake_cf_time.nc'));
  assert.deepEqual(result.warnings, []);
  const expected = ['1970-01-01T00:00:00Z', '1970-01-01T00:01:00Z'];
  assert.deepEqual(result.rows.map((row) => row.time),
    expected.flatMap((time) => Array(3).fill(time)));
  assert.deepEqual(result.rows.map(({depth, temperature, latitude, longitude}) =>
    [depth, temperature, latitude, longitude]), [
    [0, 10, 40, -70], [5, 11, 40, -70], [10, 12, 40, -70],
    [0, 20, 41, -71], [5, 21, 41, -71], [10, 22, 41, -71]
  ]);
  const validation = validate(result.rows, {
    time: 'time', latitude: 'latitude', longitude: 'longitude', depth: 'depth'
  });
  assert.deepEqual(validation.missingRequired, []);
  assert.deepEqual(validation.issues, []);
  assert.deepEqual(validation.standardizedRows.map((row) => row.time),
    result.rows.map((row) => row.time));
});

test('CF units, references, timezones, and millisecond precision are honored', async () => {
  for (const [units, times, expected] of [
    ['minutes since 2020-01-01 00:00:00', [0.5, 60.25],
      ['2020-01-01T00:00:30Z', '2020-01-01T01:00:15Z']],
    ['hours since 2020-01-01T00:00:00Z', [0, 1.5],
      ['2020-01-01T00:00:00Z', '2020-01-01T01:30:00Z']],
    ['days since 2020-01-01T00:00:00Z', [0, 1],
      ['2020-01-01T00:00:00Z', '2020-01-02T00:00:00Z']],
    ['seconds since 2020-01-01T00:00:00Z', [0.5, 60.25],
      ['2020-01-01T00:00:00.500Z', '2020-01-01T00:01:00.250Z']],
    ['days since 2020-01-01 00:00:00+02', [0, 1],
      ['2019-12-31T22:00:00Z', '2020-01-01T22:00:00Z']]
  ]) {
    const result = await parseUpload(cfFixture({units, times, calendar: 'standard'}));
    assert.deepEqual(result.warnings, [], units);
    assert.deepEqual(result.rows.map((row) => row.time),
      expected.flatMap((time) => Array(3).fill(time)), units);
    assert.deepEqual(validate(result.rows, {
      time: 'time', latitude: 'latitude', longitude: 'longitude'
    }).issues, [], units);
  }
});

test('absent CF calendar defaults to standard; ISO character times remain unchanged', async () => {
  const numeric = await parseUpload(cfFixture({noCalendar: true}));
  assert.deepEqual(numeric.warnings, []);
  assert.equal(numeric.rows[3].time, '1970-01-01T00:01:00Z');

  const strings = await parseUpload(fixture('data_intake_string_time.nc'));
  assert.deepEqual(strings.warnings, []);
  assert.deepEqual(strings.rows.map((row) => row.time),
    ['2020-01-01T00:00:00Z', '2020-01-01T00:01:00Z']);
  assert.deepEqual(validate(strings.rows, {
    time: 'time', latitude: 'latitude', longitude: 'longitude'
  }).issues, []);
});

test('invalid units and unsupported calendars never invent timestamps', async () => {
  for (const options of [
    {units: 'seconds after 1970-01-01T00:00:00Z'},
    {calendar: '360_day'},
    {units: 'seconds since 1500-01-01T00:00:00Z'},
    {times: [-123456789012, 60]}
  ]) {
    const result = await parseUpload(cfFixture(options));
    assert.match(result.warnings.join(' '), /time variable could not be decoded safely/);
    assert.deepEqual(result.rows.map((row) => row.time),
      (options.times ?? [0, 60]).flatMap((time) => Array(3).fill(time)));
    assert.match(validate(result.rows, {
      time: 'time', latitude: 'latitude', longitude: 'longitude'
    }).issues.join(' '), /malformed timestamps/);
  }
});

test('existing CSV parsing and upload safety limit remain unchanged', async () => {
  assert.deepEqual({...parseCsv('Latitude,Time\n40,2024-01-01\n')[0]},
    {latitude: '40', time: '2024-01-01'});
  await assert.rejects(parseUpload({name: 'large.nc', size: 250 * 1024 * 1024 + 1}),
    /Files larger than 250 MB/);
});
