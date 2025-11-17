# Ventilation and Internal Gains Module — README

This module implements key ISO-based methods for evaluating **heat transfer by ventilation** and **internal heat gains** in thermally conditioned and unconditioned zones.

It also includes an auxiliary function for computing **transmission heat transfer coefficients** between conditioned and adjacent zones, following **ISO 13789**.

---

## 1) Overview

The module covers three main components:

1. **Ventilation heat transfer coefficient** (`VentilationInternalGains.heat_transfer_coefficient_by_ventilation`):
   - Evaluates the **natural ventilation** rate and corresponding heat transfer coefficient (`H_ve_nat`) using **ISO 16798‑7** (wind and temperature-driven airflow).
   - Supports a simplified **occupancy-based** ventilation model.

2. **Internal heat gains** (`VentilationInternalGains.internal_gains`):
   - Computes total internal heat gains from occupants, appliances, and optionally nearby unconditioned zones, using **ISO 16798‑1** and **ISO 15316‑1** formulations.

3. **Transmission between zones** (`transmission_heat_transfer_coefficient_ISO13789`):
   - Calculates inter-zone transmission coefficients (`H_ztu_tot`, `b_ztu_m`) according to **ISO 13789**, accounting for heat exchanges between conditioned, unconditioned, and external environments.

---

## 2) Class and Function Summary

### 2.1 Dataclass: `h_natural_vent`

```python
@dataclass
class h_natural_vent:
    H_ve_nat: np.ndarray
```
Stores the ventilation heat transfer coefficient array (`H_ve_nat`, in W/K).

---

### 2.2 Class: `VentilationInternalGains`

#### Constructor
```python
VentilationInternalGains(building_object)
```
- **Parameters**
  - `building_object`: dictionary or object with building geometry and surface data (windows, net floor area, etc.).

---

### 2.3 Method: `heat_transfer_coefficient_by_ventilation(...)`

#### Purpose
Computes the **heat transfer coefficient by ventilation** (`H_ve_nat`) for the thermal zone.

#### Signature
```python
@staticmethod
def heat_transfer_coefficient_by_ventilation(
    building_object, Tz, Te, u_site,
    Rw_arg_i=None, c_air=1006, rho_air=1.204,
    C_wnd=0.001, C_st=0.0035, rho_a_ref=1.204,
    altitude=None, type_ventilation="temp_wind",
    flowrate_person=1.4
) -> h_natural_vent
```

#### Modes
1. **Natural ventilation** (`type_ventilation="temp_wind"`)
   - Based on **ISO 16798‑7 (2017)** section 6.4.3.5.4.
   - Uses wind speed (`u_site`) and indoor/outdoor temperature difference (`|Tz – Te|`) to estimate air exchange through windows.
   - Airflow rate formula:
     \n\\[ q_v = 3600 * \\frac{\\rho_{ref}}{\\rho_e} * \\frac{A_w}{2} * \\sqrt{ \\max(C_{wnd} u_{site}^2, C_{st} h_{st} |T_z - T_e|) } \\]\n
   - **Key variables:**
     - `C_wnd` (wind coefficient): 0.001 (1/m·s)
     - `C_st` (stack effect coefficient): 0.0035 ((m/s)/(m·K))
     - `h_st`: effective stack height = max(height tops) – min(height bottoms)
     - `ρ_a_ref`: reference air density at 20 °C (adjusted for altitude if provided)
     - `A_w`: effective open window area (sum over windows × opening ratio `Rw_arg_i`)

   - The heat transfer coefficient is finally computed as:
     \n\\[ H_{ve} = \\frac{c_{air} \\rho_{air} q_v}{3600} \\; [W/K] \\]\n

2. **Occupancy-based ventilation** (`type_ventilation="occupancy"`)
   - Simplified method scaling ventilation to **floor area** and **occupant activity**:
     \n\\[ H_{ve} = A_{use} (3.6·flowrate_{person}) ρ_{air} c_{air} / 3600 \\]\n
   - Typical `flowrate_person` = 1.4 l/(s·m²).

#### Returns
- `np.ndarray`: array of ventilation heat transfer coefficients (`H_ve_nat`, in W/K).

#### Notes
- Handles altitude correction for air density.
- Issues warnings if `Rw_arg_i` length does not match window count (defaults to 0.9 opening ratio).
- Supports both **window-driven** and **occupancy-driven** modes.

---

### 2.4 Method: `internal_gains(...)`

#### Purpose
Calculates **internal heat gains** to the conditioned zone according to **ISO 16798‑1** and **ISO 15316‑1**.

#### Signature
```python
def internal_gains(
    cls, building_type_class, a_use,
    unconditioned_zones_nearby=False, list_adj_zones=None,
    Fztc_ztu_m=1, b_ztu=1,
    h_occup=1, h_app=1, h_light=1, h_dhw=1,
    h_hvac=1, h_proc=1
)
```

#### Formula
\[
Φ_{int,z,t} = (q_{int,occ}·h_{occup} + q_{int,app}·h_{app})·A_{use}
\]

If **unconditioned zones** exist:
\[
Φ_{int,z,t} += Φ_{int,dir,z,t} + (1-b_{ztu})·F_{ztc,ztu,m}·Φ_{int,dir,z,t}
\]

#### Parameters
- `building_type_class`: key identifying building type (e.g. *Residential_apartment*, *Office*, etc.).
- `a_use`: usable area (m²).
- `unconditioned_zones_nearby`: whether adjacent unconditioned zones exist.
- `list_adj_zones`: number of adjacent zones.
- `Fztc_ztu_m`, `b_ztu`: ISO 13789 coupling factors for conditioned/unconditioned zone exchange.
- `h_*`: hourly activity multipliers for occupancy, appliances, lighting, etc.

#### Returns
- `float`: internal gains in watts (`Φ_int_z_t`).

---

## 3) Typical Workflow

1. **Ventilation Heat Transfer**
```python
Hve = VentilationInternalGains.heat_transfer_coefficient_by_ventilation(
    building_object=my_bui,
    Tz=21, Te=5, u_site=3.5,
    type_ventilation="temp_wind"
)
```

2. **Internal Gains**
```python
gains = VentilationInternalGains(my_bui).internal_gains(
    building_type_class="Residential_apartment",
    a_use=120,
    h_occup=0.8, h_app=0.6
)
```

---

## 4) Integration Roadmap (Future Enhancements)

- **Air leaks**: integrate infiltration losses for cracks and envelope leakage tests.
- **Cross ventilation**: include simultaneous airflow paths between opposite façades.
- **Mechanical ventilation**: handle forced air systems with user‑defined flow rates and recovery efficiency.

---

## 5) Dependencies

```bash
pip install numpy
```

- NumPy: numerical arrays and vectorized math.
- (Optional) pandas, warnings — if extending data handling.

---

## 6) References

- **ISO 52016‑1:2017**, § 6.5.10 Ventilation and Heat Transfer Coefficients  
- **ISO 16798‑7:2017**, § 6.4.3.5 Natural Ventilation Airflow  
- **ISO 16798‑1:2019**, § M1–M10 Internal Gains  
- **ISO 13789:2017**, § 7 Transmission Heat Transfer Coefficients through Adjacent Spaces

---

## License

Use and modify freely for research and educational purposes. When integrating into software distributions, ensure ISO content references are properly cited.
