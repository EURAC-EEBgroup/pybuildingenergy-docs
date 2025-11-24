
## <h1 style="color:#df1b12; margin-bottom:0px; font-weight:bold"><strong>API Reference — DHW Calculation Module </strong></h1>


## <h2 style="color:#df1b12; margin-bottom:0px; font-weight:bold"><strong>Get calendar by name</strong></h2>

```python 
def get_calendar_by_name(nation_name: str):
```

### Inputs

| Parameter | Type | Description |
|------------|------|-------------|
| `nation_name` | `str` | Human-readable nation name (e.g., "Italy", "Germany"). |

### Output
- Calendar instance exposing `is_working_day(date)` and `holidays(year)`.

### Raises
- `ValueError` if the nation cannot be resolved (ensure `workalendar` is installed and the name is valid).

---

## <h2 style="color:#df1b12; margin-bottom:0px; font-weight:bold"><strong>Generate daily calendar</strong></h2>

```python 
def generate_daily_calendar(year: int, month: int, country_calendar) -> dict
```

### Inputs

| Parameter | Type | Description |
|------------|------|-------------|
| `year`, `month`: target year and month. |
| `country_calendar`: Workalendar instance (from `get_calendar_by_name`). |

### Purpose
Generate a dict mapping **YYYY-MM-DD** → **status** (`"Working"`, `"Non-Working"`, `"Holiday"`) for a specific month/year.


### Output
- `dict`: `{ "YYYY-MM-DD": "Working|Non-Working|Holiday", ... }`.

---

## <h2 style="color:#df1b12; margin-bottom:0px; font-weight:bold"><strong>Generate calendar</strong></h2>

```python 
def generate_calendar(nation_name: str, year: int) -> pd.DataFrame
```

### Inputs

| Parameter | Type | Description |
|------------|------|-------------|
| `nation_name`: string (e.g., `"Italy"`). |
| `year`: target year. |

### Output
- `DataFrame` with columns:
  - `days`: `Timestamp` (one row per day)
  - `values`: categorical string in `{"Working","Non-Working","Holiday"}`

---

## <h2 style="color:#df1b12; margin-bottom:0px; font-weight:bold"><strong>Get daily volume</strong></h2>

```python 
def calc_V_w_day_trough_V_w_p_day(method: str = None, building_area: float = None, building_type: str = None, V_w_p_day: float = None) -> float
```

### Inputs

| Parameter | Type | Description |
|------------|------|-------------|
| `method`: `"correlation"` or `"table"`. |
| `building_area`: gross floor area [m²]. |
| `building_type`: one of `{"Single_family_house","Attached_house","Dwelling"}`. |
| `V_w_p_day`: liters/person/day (used when `method == "table"`; from B_5 modified). |

### Purpose
Compute the **daily reference volume** at reference conditions, for **dwellings**, based on **equivalent persons**.

### Parameters
- `mode`: two methods can be used: 
    1) 'number_of_person' providing the number of person' 
    2) 'building_area': providing the area of the building 
    3) 'number_of_units': provinding specific units according to the table B_4
- `method`: possible selection: 
    1) 'correlation': using correlation of B.5
    2) 'table': using table of B.5
- `building_area`: gross building area [m2]
- `building_type`: type of building, possible choice: 'Single_family_house', 'Attached_house', 'Dwelling'
- `num_person`: number of person inhabiting the dwelling
- `V_w_f_day`: value taken from the dataframe "table_b_5"
- `V_w_p_day`: value of liters of DHW per person taken from table b_5 modified

### Output
- `V_w_nd_ref` [m³/day] (daily volume need at reference conditions).

---

## <h2 style="color:#df1b12; margin-bottom:0px; font-weight:bold"><strong>Get days</strong></h2>

```python 
def get_days(year: int) -> list[int]
```

### Inputs

| Parameter | Type | Description |
|------------|------|-------------|
| `year`: integer. |

### Purpose
Return the **number of valid days per month** for the given year.

### Parameters
- `year`: integer.

**Returns**
- `list` of length 12 with day counts (e.g., `[31,28,31,...]` or `[31,29,31,...]` in leap years).

---

## <h2 style="color:#df1b12; margin-bottom:0px; font-weight:bold"><strong>Volume and energy calculation</strong></h2>

```python 

def Volume_and_energy_DHW_calculation(
    n_workdays: int,
    n_weekends: int,
    n_holidays: int,
    sum_fractions: pd.DataFrame,
    total_days: int,
    hourly_fractions: pd.DataFrame,
    teta_W_draw: float,
    teta_w_c_ref: float,
    teta_w_h_ref: float,
    teta_W_cold: float,
    mode_calc: str,
    building_type_B3: str,
    building_area: float,
    unit_count: int,
    building_type_B5: str,
    residential_typology: str,
    calculation_method: str,
    year: int,
    country_calendar: pd.DataFrame
    ) -> Tuple
```

### Inputs

| Parameter | Type | Description |
|------------|------|-------------|
| `n_workdays`, `n_weekends`, `n_holidays`: calendar counts. |
| `sum_fractions`: DataFrame of summed hourly fractions. |
| `total_days`: total days in the year. |
| `hourly_fractions`: hourly distribution per day type. |
| `teta_W_draw`, `teta_w_c_ref`, `teta_w_h_ref`, `teta_W_cold`: temperature parameters [°C]. |
| `mode_calc`: `'area' | 'number_of_units' | 'volume_type_bui'`. |
| `building_type_B3`, `building_type_B5`: EPB classification strings. |
| `residential_typology`: key from table B_5 modified. |
| `building_area`, `unit_count`, `calculation_method`, `year`, `country_calendar`: additional parameters. |

### Purpose
Core routine computing **daily**, **monthly**, and **yearly** DHW **volume** and **energy** needs for a target building and usage.

### Output
- `yearly_cons`: yearly energy [kWh]
- `V_W_nd_d`: daily volume [m³]
- `monthly_volume`: list[float] monthly volumes [m³]
- `yearly_volume`: total yearly volume [m³]
- `Q_W_nd_d`: daily energy [kWh]
- `V_W_nd_h_i`: hourly volume DataFrame
- `daily_cons_volume`: list[float] hourly volume per day type
- `daily_cons_energy`: list[float] hourly energy per day type

### Raises
- `ValueError` for invalid modes or types.

---
