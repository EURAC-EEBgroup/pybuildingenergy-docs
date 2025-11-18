
## <h1 style="color:#df1b12; margin-bottom:0px; font-weight:bold"><strong>Building Input (BUI) Structure </strong></h1>


This document explains the **BUI** (Building Input) dictionary used for ISO 52016 simulations.  
It defines the building geometry, surfaces, (general)systems, and operational parameters required to calculate hourly temperatures and energy needs.

---
## <h2 style="color:#df1b12; margin-bottom:0px; font-weight:bold"><strong>Structure Overview</strong></h2>

```python
BUI = {
    "building": {...},
    "adjacent_zones": [...],
    "building_surface": [...],
    "units": {...},
    "building_parameters": {...}
}
```


!!! Note
    The type of the surface has been mapped in the calculation using the following code:

    - `OP`: Opaque element
    - `W`: Transparent element
    - `GR`: Ground-contact element
    - `AD`: Adiabatic element
    - `ADJ`: Adjacent element

    ```python
    ...
    for i, surf in enumerate(building_object["building_surface"]):
        if surf["type"] == "opaque":
            if surf["sky_view_factor"] == 0:
                typology_elements[i] = "GR"
            else:
                typology_elements[i] = "OP"
        elif surf["type"] == "adiabatic":
            typology_elements[i] = "AD"
        elif surf["type"] == "transparent":
            typology_elements[i] = "W"
        elif surf["type"] == "adjacent":
            typology_elements[i] = "ADJ"
        surf["ISO52016_type_string"] = typology_elements[i]
    ```

---

## <h2 style="color:#df1b12; margin-bottom:0px; font-weight:bold"><strong>Main Building Metadata: `"building"`</strong></h2> 


| Key | Type | Description |
|------|------|-------------|
| `name` | str | Building name or identifier. |
| `azimuth_relative_to_true_north` | float (°) | Orientation of the building relative to north.  (0=N, 90=E, 180=S, 270=W)|
| `latitude`, `longitude` | float | Coordinates (used for weather and solar position). |
| `exposed_perimeter` | float (m) | External perimeter. |
| `height` | float (m) | Building height (floor to roof). |
| `wall_thickness` | float (m) | Average wall layer total thickness  |
| `n_floors` | int | Number of floors. |
| `building_type_class` | str | Type of building (e.g., *Residential_apartment*, *Office*). |
| `adj_zones_present` | bool | Whether unconditioned/adjacent zones exist. |
| `number_adj_zone` | int | Number of adjacent zones. |
| `net_floor_area` | float (m²) | Conditioned floor area. |
| `construction_class` | str | Construction quality (e.g., *class_i*). |


---

## <h2 style="color:#df1b12; margin-bottom:0px; font-weight:bold"><strong>Adjoining/Unconditioned Spaces: `"adjacent_zones"`</strong></h2> 

Defines zones adjacent to the conditioned area, used for ISO 13789 transmission heat transfer.

Each zone has:

| Key | Description |
|------|-------------|
| `name` | Zone name. |
| `orientation_zone.azimuth` | local azimuth of each adjacent unconditioned zone (°). |
| `area_facade_elements` | Areas of façade elements (array, m²). |
| `typology_elements` | Element types: `OP` (opaque), `GR` (ground), etc. |
| `transmittance_U_elements` | U-values of each element (W/m²K). |
| `orientation_elements` | orientation code by element: `NV` North-vertical (≈0°), `SV` South-vertical (≈180°),`EV` East-vertical (≈90°),  `WV` West-vertical (≈270°),`HOR` horizontal (roof/slab). |
| `volume` | Zone air volume (m³). |
| `building_type_class` | Type of building zone (same taxonomy). |
| `a_use` | useful area of the adjacent zone . |

---

## <h2 style="color:#df1b12; margin-bottom:0px; font-weight:bold"><strong>Envelope Elements: `"building_surface"`</strong></h2> 

Describes all external and internal surfaces forming the building envelope.

### Common attributes
| Key | Description |
|------|-------------|
| `name` | Surface name. |
| `type` | `"opaque"`, `"transparent"`, `"adiabatic"`, `"adjacent"`. |
| `area` | Surface area (m²). |
| `sky_view_factor` | Fraction of visible sky (0–1). |
| `u_value` | Thermal transmittance (W/m²K). |
| `solar_absorptance` | Fraction of solar radiation absorbed (0–1). |
| `thermal_capacity` | Surface thermal capacity (J/K). |
| `orientation.azimuth` | Azimuth (0 = N, 90 = E, 180 = S, 270 = W). |
| `orientation.tilt` | Tilt angle (0 = horizontal, 90 = vertical). |
| `name_adj_zone` | Linked adjacent zone (if applicable). |

### Transparent surfaces
Include window-specific attributes:
| Key | Description |
|------|-------------|
| `g_value` | Solar transmittance of glazing. |
| `height`, `width` | Window dimensions (m). |
| `parapet` | Window sill height above floor (m). |
| `shading`, `shading_type` | Boolean and type of shading (e.g., *horizontal_overhang*). |
| `width_or_distance_of_shading_elements` | Distance or overhang width. |
| `overhang_proprieties` | Additional geometric data for shading devices. |

---

## <h2 style="color:#df1b12; margin-bottom:0px; font-weight:bold"><strong>Unit Definitions: `"units"`</strong></h2> 

Defines unit conventions for each physical quantity.

| Key | Example | Meaning |
|------|----------|----------|
| `area` | `"m²"` | Surface area unit. |
| `u_value` | `"W/m²K"` | Heat transmittance. |
| `thermal_capacity` | `"J/kgK"` | Heat storage capacity. |
| `azimuth`, `tilt` | `"degrees"` | Orientation conventions. |
| `internal_gain` | `"W/m²"` | Internal gain density. |
| `internal_gain_profile` | `"Normalized 0–1"` | Profile normalization rule. |
| `HVAC_profile` | `"0: off, 1: on"` | HVAC operating schedule encoding. |

---

## <h2 style="color:#df1b12; margin-bottom:0px; font-weight:bold"><strong>Thermal, System, and Operational Settings: `"building_parameters"`</strong></h2> 

### Temperature Setpoints
| Key | Description |
|------|-------------|
| `heating_setpoint`, `heating_setback` | Comfort and setback temperatures (°C). |
| `cooling_setpoint`, `cooling_setback` | Cooling comfort and setback (°C). |
| `units` | `"°C"`. |

### System Capacities
| Key | Description |
|------|-------------|
| `heating_capacity`, `cooling_capacity` | Maximum system capacities (W). |
| `units` | `"W"`. |

### Airflow Rates
| Key | Description |
|------|-------------|
| `infiltration_rate` | Airflow in air changes per hour (ACH). |
| `units` | `"ACH"`. |

### Internal Gains
Each internal source (occupants, appliances, lighting) defines:
| Key | Description |
|------|-------------|
| `name` | Gain type. |
| `full_load` | Peak power density (W/m²). |
| `weekday`, `weekend` | 24-hour normalized (0–1) schedules. |

### Construction
| Key | Description |
|------|-------------|
| `wall_thickness` | Wall thickness (m). |
| `thermal_bridges` | Linear thermal bridge coefficient (W/m·K). |

### Climate Parameters
| Key | Description |
|------|-------------|
| `coldest_month` | Index of coldest month (1 = Jan, 12 = Dec). |

### HVAC and Ventilation Profiles
Hourly normalized profiles for system operation:

| Profile | Description |
|----------|-------------|
| `heating_profile` | 24‑hour on/off (0–1) heating activity. |
| `cooling_profile` | 24‑hour on/off cooling activity. |
| `ventilation_profile` | 24‑hour on/off ventilation schedule. |

---

## <h2 style="color:#df1b12; margin-bottom:0px; font-weight:bold"><strong>Example Workflow</strong></h2>

```python
from iso52016 import ISO52016

# Validate input
bui_checked, issues = ISO52016.sanitize_and_validate_BUI(BUI, fix=True)

# Run hourly energy needs
hourly, annual = ISO52016.Temperature_and_Energy_needs_calculation(
    bui_checked, weather_source="pvgis"
)

print(annual)
```

---

## <h2 style="color:#df1b12; margin-bottom:0px; font-weight:bold"><strong>Good Practices</strong></h2>

- Always verify **units** and **orientation angles** before running simulations.  
- Ensure **surface U-values** and **areas** are consistent with geometry.  
- Normalize all **profiles** (0–1).  
- When `adj_zones_present` is `True`, populate valid adjacent zone data.  
- Latitude/longitude and azimuth are essential for solar radiation accuracy.

---

## <h2 style="color:#df1b12; margin-bottom:0px; font-weight:bold"><strong>Outputs of ISO 52016</strong></h2>

After running the calculation, typical outputs include:
- Hourly heating/cooling needs (`Q_HC`, W)
- Operative temperature (`T_op`, °C)
- External temperature (`T_ext`, °C)
- Annual heating/cooling energy (Wh/m²)

---

## <h2 style="color:#df1b12; margin-bottom:0px; font-weight:bold"><strong>Static data & constants: `global_inputs.py` </strong></h2>

### Purpose

- Provide **reference tables** (e.g., ISO 13789 `n_ue` air-tightness classes) and **thermophysical constants**.
- Contain an **emitter table** `TB14` (ΔT exponents).

### Key Objects

- `periods`, `bui_types`, `months`: taxonomies.
- `WATER_DENSITY = 1000` `[kg·m⁻³]`
- `WATER_SPECIFIC_HEAT_CAPACITY = 0.00116` `[kWh·kg⁻¹·K⁻¹]` (→ multiply by `kg` and `ΔT` to get kWh)
- `df_n_ue` — ISO 13789:2018 (Table 7) **conventional air change rate** between unconditioned space and exterior:

| code | description (air-tightness) | `n_ue` [h⁻¹] |
|------|-----------------------------|--------------|
| 1 | No doors/windows openings | 0.1 |
| 2 | All joints well sealed, no openings | 0.5 |
| 3 | Well sealed, small openings | 1.0 |
| 4 | Some localized open joints | 3.0 |
| 5 | Numerous open joints / large openings | 10.0 |

- `TB14` — emitter exponents and nominal ΔT:
    - Radiator: `n=1.3`, `Δθ_air=50°C`, `Δθ_water=20°C`
    - Floor heating: `n=1.1`, `Δθ_air=15°C`, `Δθ_water=5°C`
    - Fan coil: `n=1.0`, `Δθ_air=25°C`, `Δθ_water=10°C`


### Usage & Physics

- `n_ue` maps directly into **adjacent unconditioned zone ventilation** (see §4.3), i.e. `que = V_u · n_ue` `[m³·h⁻¹]`.
- Water constants are useful for DHW/emitters energy conversions (not used inside `ventilation.py` yet).

---

## <h2 style="color:#df1b12; margin-bottom:0px; font-weight:bold"><strong>Implementation Notes & Robustness</strong></h2>

- **Type safety**: many arrays in `BUI` are `dtype=object`. Cast to `np.asarray(..., dtype=float)` before algebra.
- **Orientation logic**: To identify interface elements for \(H_{d,zt{\text -}ztu}\), define a **clear mapping** between `building_surface[*].name_adj_zone` and the `adjacent_zones[*].name` and use that to split \(\mathcal{E}_{zt{\text -}ztu}\) vs \(\mathcal{E}_{ztu{\text -}ext}\). Avoid relying only on cardinal labels like `NV/SV/...` when adjacency is explicit in the `BUI`.
- **Units consistency**: Eq. (4.12b) uses the common shortcut `0.33` `[Wh·m⁻³·K⁻¹]` for flows in m³·h⁻¹. If you operate on SI `[s]`, convert accordingly \( \frac{\rho c}{3600} \).
- **Altitude**: The simple density correction used in Eq. (4.2) is adequate for building simulation. For high-altitude sites you may want a full barometric formula.

---
