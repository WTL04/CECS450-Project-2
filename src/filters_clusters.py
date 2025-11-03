"""
Wrapper for magnitude, depth, and county filters.
Keeps map lightweight with dynamic sampling and compatible with magnitude slider.
"""

from .filters_magnitude import add_magnitude_filters
from .filters_depth import add_depth_filters
from .filters_region import add_region_filters


def _dynamic_limits(n):
    if n >= 300_000:
        return (350, 350, 300)
    if n >= 150_000:
        return (450, 450, 350)
    if n >= 75_000:
        return (550, 550, 400)
    return (650, 650, 500)


def add_filtered_layers(m, df, mag_sample=None, depth_sample=None, region_sample=None):
    n = len(df)
    dyn_mag, dyn_depth, dyn_region = _dynamic_limits(n)
    mag_cap = mag_sample or dyn_mag
    depth_cap = depth_sample or dyn_depth
    region_cap = region_sample or dyn_region

    print(f"[filters] dataset={n:,} -> caps: mag={mag_cap}, depth={depth_cap}, county={region_cap}")

    # Magnitude (includes slider)
    add_magnitude_filters(m, df, sample_limit=mag_cap)

    # Depth filters
    add_depth_filters(m, df, sample_limit=depth_cap)

    # Regional filters
    add_region_filters(m, df, sample_limit=region_cap)

    print("[filters] all layers + slider ready.")
