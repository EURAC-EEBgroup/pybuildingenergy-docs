# Category profile

**Occupancts, Lighting, Appliance, Ventilation, Heating, Cooling profile**
---
```python
def generate_category_profile(
    cls,
    building_object,
    occupants_schedule_workdays,
    occupants_schedule_weekend,
    appliances_schedule_workdays,
    appliances_schedule_weekend,
    lighting_schedule_workdays,
    lighting_schedule_weekend,
)
```

---


### Inputs

| Parameter | Type | Description |
|------------|------|-------------|
| `building_object` | `dict` | Building model containing `building_type_class` and optional internal gain profiles. |
| `occupants_schedule_workdays/weekend` | `dict[str, list[float]]` | Default hourly occupancy profiles (24 values each). |
| `appliances_schedule_workdays/weekend` | `dict[str, list[float]]` | Default hourly appliance profiles. |
| `lighting_schedule_workdays/weekend` | `dict[str, list[float]]` | Default hourly lighting profiles. |

---


### Purpose

In building energy simulations — especially those following **ISO 52016-1:2017** (Energy needs for heating and cooling, internal temperatures, and loads) or the broader **EPB** (Energy Performance of Buildings) framework — each thermal zone requires **hourly profiles** for occupancy, lighting, appliances, ventilation, heating, and cooling.  

These profiles describe the **temporal behavior** of internal gains and system operation (e.g., when people are present, when lights are on, or when HVAC is active).  
This function automates the generation of such profiles by merging **custom schedules** (if defined within a building object) with **default type-based schedules**, ensuring every category has a valid 24-hour pattern.

The default type-based schedules are define in the file: `table_iso_16798_1.py`, where typical profile are getting from the EN ISO 16798-1 standard.

`generate_category_profile()` builds a consistent set of **hourly category profiles** (weekday/weekend) for:
- Occupancy  
- Appliances  
- Lighting  
- Ventilation  
- Heating  
- Cooling  

It ensures that all schedules are properly defined, validated, and ready for use in **energy balance, comfort, or control** simulations.

**How it works?**

1. **Identify building type**  
   Extracts the `building_type_class` from the input object to determine which default schedules to use.

2. **Load or fallback for each category**  
   - For **occupants**, **appliances**, and **lighting**:  
     If custom 24-hour profiles exist in `building_object["building_parameters"]["internal_gains"]`, they are used directly.  
     Otherwise, defaults are taken from the provided schedule dictionaries.
   - For **ventilation**, **heating**, and **cooling**:  
     If no profiles are defined in the building object, they **inherit the occupancy schedule** as a fallback.

3. **Validation**  
   Ensures that every schedule contains exactly **24 hourly values** (one per hour of the day).

4. **Output assembly**  
   Returns all category profiles in a structured dictionary format.

---

### Outputs
`dict` — A complete set of hourly category profiles for use in thermal simulations, HVAC control logic, or internal gain estimation.

```python
{
    "ventilation": {"weekday": array(24), "holiday": array(24)},
    "heating":     {"weekday": array(24), "holiday": array(24)},
    "cooling":     {"weekday": array(24), "holiday": array(24)},
    "occupancy":   {"weekday": array(24), "holiday": array(24)},
    "lighting":    {"weekday": array(24), "holiday": array(24)},
    "appliances":  {"weekday": array(24), "holiday": array(24)},
}
```

Each category contains **24 hourly fractions** for weekdays and weekends (holidays), typically in the range 0–1 or as relative intensity values.

---

### Example

```python
profiles = generate_category_profile(
    building_object=my_building,
    occupants_schedule_workdays=OCCUPANTS_WD,
    occupants_schedule_weekend=OCCUPANTS_WE,
    appliances_schedule_workdays=APPLIANCES_WD,
    appliances_schedule_weekend=APPLIANCES_WE,
    lighting_schedule_workdays=LIGHTING_WD,
    lighting_schedule_weekend=LIGHTING_WE,
)

# Example: access weekday lighting profile
lighting_profile = profiles["lighting"]["weekday"]
```

---

### Notes
- All profiles **must contain exactly 24 numeric values**.  
- Missing **ventilation**, **heating**, or **cooling** profiles automatically default to the **occupancy** profile.  
- Works as a preprocessing step to ensure that all internal gain and system schedules are complete and consistent before running the energy balance.
- This function is typically used in the **preprocessing pipeline** before running a dynamic energy simulation:


The `**generate_category_profile()**` is based on the following functions:

- `get_country_code_from_latlon`
- `HourlyProfileGenerator`

---

**Country code for calendar data**
---
```python
def get_country_code_from_latlon(lat: float, lon: float, default: str = "IT") -> str
```
### Parameters
- `lat`, `lon` *(float)*: Geographic coordinates.
- `default` *(str)*: Fallback code returned on errors or when the API does not return a country code. Default is `"IT"`.

### Purpose
Resolve a latitude/longitude to an ISO 3166-1 alpha-2 country code, using a reverse‑geocoding API (example: OpenCage).

**How it works:**
1. Builds a request to the OpenCage API endpoint:
   - `https://api.opencagedata.com/geocode/v1/json`
2. Sends the request with your API key (`YOUR_OPENCAGE_API_KEY` placeholder).
3. On success: extracts `ISO_3166-1_alpha2` from the first result’s `components`.
4. On any failure (HTTP ≠ 200, empty results, missing code): returns `default`.

### Notes & Best Practices
- **API Key:** Replace `"YOUR_OPENCAGE_API_KEY"` with a valid key (environment variable recommended).
- **Rate Limits:** Respect your provider’s quota; implement caching if calling repeatedly.
- **Fallback:** Consider logging when the function falls back to `default` so you can inspect geocoding issues later.
- **Alternative providers:** You can switch to other reverse‑geocoding services (Nominatim, Google, etc.) by adjusting the request/response handling.

---

**Generate hourly profiles**
---
```python
class HourlyProfileGenerator(
    country: str = "IT",
    num_months: int = 13,
    start_year: int | None = None,
    working_day_profile: np.ndarray | None = None,
    holiday_profile: np.ndarray | None = None,
    category_profiles: dict | None = None
)
```
### Inputs
- `country`: ISO 2-letter country code used by `holidays` to determine national holidays.
- `num_months`: How many months to generate (default: `13`).
- `start_year`: Starting year for the window. If `None`, uses the previous calendar year for the December start.
- `working_day_profile`, `holiday_profile`: Optional 24‑hour arrays to replace the built‑in defaults for **all** categories when `category_profiles` is omitted.
- `category_profiles`: A dict providing per‑category profiles. Each value can be:
  - a single 24‑array → applied to both weekday and holiday/weekend; or
  - a **pair** `(weekday_24, holiday_24)`; or
  - a **dict** `{ 'weekday': weekday_24, 'holiday': holiday_24 }`.

**Categories:** `("ventilation", "heating", "cooling", "occupancy", "lighting", "appliances")`

### Purpose
Generate a **continuous hourly DataFrame** (default: 13 months) with calendar flags (working day / weekend / holiday) and **per‑category normalized profiles** (0..1) for:
`ventilation`, `heating`, `cooling`, `occupancy`, `lighting`, `appliances`.

**Key Concepts**
- **Time span:** starts at `December 1st` of `start_year` (or previous year if `None`) and covers `num_months` months (default 13).
- **Calendar logic:** weekend = Saturday or Sunday; holiday set via the `holidays` library using `country`.
- **Profiles (0..1):** Per-category 24‑value arrays are mapped to each hour of the day, switching between **weekday** and **holiday/weekend** versions.
- **Retro‑compatibility:** If `category_profiles` is not provided, two default 24‑hour arrays (one for working days, one for holidays) are used for all categories. You can also pass legacy `working_day_profile`/`holiday_profile` to override those defaults.

---
### Outputs 

`generate()` returns a `pandas.DataFrame` with columns:

- `datetime`: hourly timestamps (timezone‑naive).
- `date`, `hour`, `day_of_week`, `day_name`: common time breakdowns.
- `is_holiday`, `is_weekend`, `is_working_day`, `holiday_name`.
- One column per category: `"{category}_profile"` (values in 0..1).
- `profile_value`: retro‑compatibility alias (uses `occupancy_profile`).
- `day_type`: `"Working Day"` or `"Holiday/Weekend"`.

---


### Examples

#### A) Minimal generation
```python
from profiles import HourlyProfileGenerator

gen = HourlyProfileGenerator(country="IT")
df = gen.generate()
gen.get_summary()

# Inspect first rows
print(df.head())
```

#### B) Custom per‑category profiles
```python
import numpy as np

v_wd = np.array([0]*6 + [1]*10 + [0.5]*8, dtype=float)      # ventilation - weekday
v_hd = np.array([0]*8 + [0.5]*8 + [0]*8, dtype=float)       # ventilation - holiday/weekend
occ_24 = np.array([1,1,1,1,1,1,0.5,0.5,0.5,0.1,0.1,0.1,0.2,0.2,0.2,0.2,0.5,0.5,0.5,0.8,0.8,0.8,1,1], dtype=float)

category_profiles = {
    "ventilation": {"weekday": v_wd, "holiday": v_hd},
    "occupancy": occ_24,  # same WD/HD
    # other categories will use defaults
}

gen = HourlyProfileGenerator(country="DE", category_profiles=category_profiles)
df = gen.generate()
```

#### C) Plot daily averages with weekend/holiday shading
```python
fig = gen.plot_annual_profiles(
    categories=["ventilation", "occupancy", "lighting"],
    freq="D",
    include_weekend_shading=True,
    title="Annual Profiles — Daily Averages"
)
fig.show()
```

#### D) Resolve a country code from coordinates
```python
from profiles import get_country_code_from_latlon
code = get_country_code_from_latlon(46.49, 11.33, default="IT")
print(code)  # e.g., "IT" or fallback
```

## Error Handling, Edge Cases and Validation
- **Invalid profile shapes**: raises `ValueError` for any 24‑hour array not equal to `(24,)`.
- **Geocoding failures**: returns the `default` country code; consider logging or retry strategies.
- **Missing `generate()`**: `get_summary()` / `plot_annual_profiles()` will raise if called before `generate()`.
- **Holiday calendars**: ensure `country` is supported by `holidays`; for custom calendars, precompute a boolean series and merge it into the DataFrame.
- Every 24‑array is validated to **exactly 24 elements**; otherwise a `ValueError` is raised.


---

