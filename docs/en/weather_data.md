# Weather Data

```python
def Weather_data_bui(cls, building_object, path_weather_file, weather_source="pvgis") -> simulation_df
```   

### Parameters
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `building_object` | `dict` | — | Building data structure used by the ISO 52010 routine for site/geometry context. |
| `path_weather_file` | `str | PathLike` | — | Path to the **EPW** file, e.g., `../User/documents/epw/athens.epw`. |
| `weather_source` | `str` | `"pvgis"` | Weather pipeline selector. Supported values: `"pvgis"`, `"epw"`. (Both branches currently call the same processor.) |

---

### Purpose
Fetches and prepares **weather time series** for a building simulation by invoking an ISO 52010-compliant pre-processor and returning a small wrapper that carries the resulting `pandas.DataFrame`.

The weather data can be retrieved in two ways:

1. through the pvgis website `(https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis_en)`. In this case, you only need to provide the latitude and longitude of the site to retrieve the data directly from the pvgis API
2. through a file epw. The user can provide a meteo file type epw downloadable also from: `https://www.ladybug.tools/epwmap/`


### How it works:

1. **Calls the ISO 52010 pipeline**  
   ```python
   Calculation_ISO_52010(building_object, path_weather_file, weather_source=weather_source).sim_df
   ```
   wraps the result in a `pandas.DataFrame` called `sim_df`.
2. **Ensures a proper time index**  
   Casts the index to a `pd.DatetimeIndex`, so downstream code can rely on hourly timestamps.
3. **Returns a lightweight wrapper**  
   ```python
   return simulation_df(simulation_df=sim_df)
   ```

---

### Output
| Type | Description |
|------|-------------|
| `simulation_df` | Wrapper object containing `simulation_df=sim_df`, where `sim_df` is a `pandas.DataFrame` indexed by `DatetimeIndex` with the weather variables produced by the ISO 52010 workflow. |

---

### Typical `sim_df` Columns

Exact columns depend on your `Calculation_ISO_52010` implementation, but commonly include:

- Dry-bulb temperature, relative humidity, wind speed
- Solar irradiance terms (e.g., direct/diffuse/global or plane-of-array)
- Sky temperature / longwave terms if modeled

> Non-weather operational drivers (occupancy, setpoints) are **not** constructed here; this function only prepares weather data.

---

### Notes

- `weather_source="pvgis"` and `weather_source="epw"` currently execute the **same** code path. Add branching logic later if you need different parsing or metadata handling.
- The index is expected to be **continuous hourly**. If your EPW contains gaps or DST shifts, ensure the ISO 52010 routine resolves them.
- Units follow standard EPW / ISO 52010 conventions (°C, W/m², m/s, %). Verify if you add custom variables.

---

### Example

```python
sim = Weather_data_bui(
    building_object=my_building,
    path_weather_file="../data/weather/rome.epw",
    weather_source="epw",
)
df = sim.simulation_df            # unwrap the DataFrame
print(df.index[:24])              # first day (hourly)
print(df.columns.tolist()[:8])    # peek at columns
```

---

### Reference

- **EN ISO 52010-1** – Calculation of solar & daylight quantities for building energy needs
- Project class/type: `simulation_df`
- Weather preprocessing class: `Calculation_ISO_52010`
