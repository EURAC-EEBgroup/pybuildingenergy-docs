# `Weather_data_bui(building_object, path_weather_file, weather_source="pvgis")`

### Purpose
Builds the **simulation input time series** (hourly index) by combining **weather** (via ISO 52010 preprocessing) with **operational profiles** for:
- Internal gains (through *occupancy level* scalars)
- Ventilation/comfort (through *comfort level* scalars)
- Heating & cooling **setpoints** and **setbacks** (weekday/weekend logic)

The output is a single `DataFrame` usable as a driver for dynamic energy calculations.

---

### 📘 Function Signature
```python
def Weather_data_bui(cls, building_object, path_weather_file, weather_source="pvgis") -> simulation_df
```

---

### 📥 Parameters
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `building_object` | `dict` | — | Building data structure created via `Building` or `Buildings_from_dictionary`. Must include the operational fields listed below. |
| `path_weather_file` | `str | PathLike` | — | Path to the **EPW** weather file (e.g., `../User/documents/epw/athens.epw`). Used as the source for ISO 52010 processing. |
| `weather_source` | `str` | `"pvgis"` | Source for weather processing. Supported: `"pvgis"` or `"epw"`. Both branches call `Calculation_ISO_52010(...).sim_df`. |

---

### ✅ Required Fields in `building_object`
These keys are read to construct weekday/weekend schedules and setpoints. *Examples in brackets*:

- `occ_level_wd`: occupancy **scaling** profile for **workdays** (e.g., 0–1 array)  
- `occ_level_we`: occupancy **scaling** profile for **weekends**  
- `comf_level_wd`: ventilation/comfort **scaling** profile for **workdays**  
- `comf_level_we`: ventilation/comfort **scaling** profile for **weekends**  
- `heating_setpoint`: e.g., `20` (°C)  
- `heating_setback`: e.g., `10` (°C)  
- `cooling_setpoint`: e.g., `26` (°C)  
- `cooling_setback`: e.g., `20` (°C)

> These profiles are typically **24-element arrays** (hourly) applied per weekday/weekend; monthly or seasonal variants can be handled upstream if needed.

---

### 🧠 What the Function Does
1. **Weather preprocessing (ISO 52010):**  
   Calls `Calculation_ISO_52010(building_object, path_weather_file, weather_source).sim_df` and wraps the result as a `pandas.DataFrame`.
2. **Datetime index:**  
   The resulting `DataFrame` index is coerced to a `pd.DatetimeIndex` (hourly).
3. **Return object:**  
   Returns a wrapper `simulation_df(simulation_df=sim_df)` exposing the preprocessed time series for the rest of the simulation pipeline.

---

### 📤 Returns
| Type | Description |
|------|-------------|
| `simulation_df` | A simple wrapper object holding `simulation_df=sim_df`, where `sim_df` is an hourly `pandas.DataFrame` with weather variables (ISO 52010 processed) and operational fields (occupancy/comfort scalars and setpoints/setbacks). |

---

### 📑 Typical Contents of `sim_df`
Exact columns depend on your `Calculation_ISO_52010` implementation and template, but they commonly include:

- **Weather (ISO 52010):** outdoor dry-bulb temperature, direct/diffuse/global irradiance (plane-of-array as applicable), wind speed, relative humidity, etc.  
- **Operational scalars:** `occ_level` and `comf_level` per timestamp (derived from `*_wd`/`*_we`)  
- **HVAC controls:** `heating_setpoint`, `heating_setback`, `cooling_setpoint`, `cooling_setback`

> If your pipeline attaches weekday/weekend profiles later, these may be added downstream; otherwise enrich `sim_df` at this stage.

---

### 🧩 Notes & Assumptions
- `weather_source="pvgis"` and `weather_source="epw"` currently execute **the same code path**, both using `Calculation_ISO_52010(...).sim_df`. If source-specific logic is needed (e.g., PVGIS metadata vs raw EPW), add a dedicated branch.  
- The function **does not** perform unit conversion on setpoints; ensure temperatures are in **°C** and schedules are unitless fractions (0–1).  
- The `DatetimeIndex` in `sim_df` must be **continuous hourly**; fill gaps upstream if the EPW file is incomplete.  
- Holiday/special-day profiles are not handled here; plug them in upstream/downstream if required.

---

### 🧪 Example
```python
sim = Weather_data_bui(
    building_object=my_building,
    path_weather_file="../data/weather/rome.epw",
    weather_source="epw"
)
df = sim.simulation_df  # unwrap if your wrapper exposes as attribute
print(df.index[:24])    # first day (hourly)
print(df.columns)       # check available drivers
```

---

### 🚨 Error Handling Tips
- **Missing keys in `building_object`:** validate profiles and setpoints before calling.  
- **Bad EPW path:** verify `path_weather_file` exists and is a valid EPW.  
- **Timezone/daylight saving:** ensure the ISO 52010 routine aligns the index with local convention if needed.  

---

### 📚 Related
- `Calculation_ISO_52010`: solar geometry & irradiance processing per EN ISO 52010-1.  
- Occupancy & ventilation schedule builders used to form `occ_level` and `comf_level`.  
