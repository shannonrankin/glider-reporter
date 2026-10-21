---
id: setup_map_axes_py
name: Glider Track Map Axes (Python)
description: Prepares a Cartopy map for plotting glider tracks with coastlines and labeled geographic gridlines.
language: Python
execution_instructions: Requires matplotlib and cartopy. Pass a Cartopy GeoAxes, a [west, east, south, north] extent, and plot longitude and latitude tracks on the returned axis.
required_fields:
  - latitude
  - longitude
output_type: Figure/Plot
translation_status: ready
citation: "Adapted from the PAM-Glider Noise Profiler plotting utilities: https://github.com/jeengdahl97/noise-fx-calc/blob/c2334e4dfcb66604dfa958d8aee554752f8f1b4e/noise_utils.py"
issue_url: https://github.com/shannonrankin/glider-reporter/issues/38
---

## Code

```python
import cartopy.crs as ccrs
import cartopy.feature as cfeature


def setup_map_axes(ax, extent, left_labels=True):
    """Configure a Plate Carree map axis for glider-track plots."""
    ax.set_extent(extent, crs=ccrs.PlateCarree())
    try:
        land = cfeature.NaturalEarthFeature(
            "physical", "land", "10m", edgecolor="face", facecolor="lightgray"
        )
        list(land.geometries())
        ax.add_feature(land)
        ax.add_feature(cfeature.COASTLINE.with_scale("10m"))
    except Exception as error:
        print(f"Could not load land and coastline data: {error}")
    gridlines = ax.gridlines(
        draw_labels=True,
        linewidth=0.3,
        color="gray",
        alpha=0.5,
        linestyle="--",
    )
    gridlines.top_labels = False
    gridlines.right_labels = False
    gridlines.left_labels = left_labels
    return ax
```
