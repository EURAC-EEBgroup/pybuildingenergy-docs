# Ventilation, Internal Gains and Transmission Heat Transfer between Adjacent Zones

This module implements methods for evaluating **heat transfer by ventilation** and **internal heat gains** in thermally conditioned and unconditioned zones.

It also includes an auxiliary function for computing **transmission heat transfer coefficients** between conditioned and adjacent zones, following **ISO 13789**.

---

## Overview

The module covers three main components:

1. **Ventilation heat transfer coefficient** (`VentilationInternalGains.heat_transfer_coefficient_by_ventilation`):
   - Evaluates the **natural ventilation** rate and corresponding heat transfer coefficient (`H_ve_nat`) using **ISO 16798‑7** (wind and temperature-driven airflow).
   - Supports a simplified **occupancy-based** ventilation model.

2. **Internal heat gains** (`VentilationInternalGains.internal_gains`):
   - Computes total internal heat gains from occupants, appliances, and optionally nearby unconditioned zones, using **ISO 16798‑1** and **ISO 15316‑1** formulations.

3. **Transmission between zones** (`transmission_heat_transfer_coefficient_ISO13789`):
   - Calculates inter-zone transmission coefficients (`H_ztu_tot`, `b_ztu_m`) according to **ISO 13789**, accounting for heat exchanges between conditioned, unconditioned, and external environments.

---

## Class and Function Summary

### Dataclass: `h_natural_vent`

```python
@dataclass
class h_natural_vent:
    H_ve_nat: np.ndarray
```
Stores the ventilation heat transfer coefficient array (`H_ve_nat`, in W/K).

---

### Class: `VentilationInternalGains`

#### Constructor
```python
VentilationInternalGains(building_object)
```
- **Parameters**
  - `building_object`: dictionary or object with building geometry and surface data (windows, net floor area, etc.).

---

### Functions

Function:    `heat_transfer_coefficient_by_ventilation(...)`  
---

**Physical purpose**: compute the **ventilation heat transfer coefficient** \(H_{ve}\) `[W·K⁻¹]` of the thermal zone either:
- from **natural ventilation** (ISO 16798-7:2017, single-sided airing via windows, wind/stack), or
- from **occupancy-driven flow** (simplified volumetric rate per floor area).

#### Signature
```python
@staticmethod
def heat_transfer_coefficient_by_ventilation(
    building_object, Tz, Te, u_site, Rw_arg_i=None, c_air=1006, 
    rho_air=1.204, C_wnd=0.001, C_st=0.0035, rho_a_ref=1.204, altitude=None,
    type_ventilation="temp_wind", flowrate_person=1.4
) -> h_natural_vent:
```

#### Inputs (main)
- `Tz` `[°C]` indoor air temperature (zone).
- `Te` `[°C]` outdoor air temperature.
- `u_site` `[m·s⁻¹]` local wind speed at site height (as per ISO 16798-7 assumptions).
- `Rw_arg_i` `[-]` array of **opening ratios** per window (`0…1`). If `None`, defaults to `0.9`.
- `C_wnd = 0.001` `[(m·s⁻¹)⁻¹]` wind coefficient (ISO 16798-7 Table 11).
- `C_st = 0.0035` `[(m·s⁻¹)/(m·K)]` stack coefficient (ISO 16798-7 Table 11).
- `rho_a_ref` `[kg·m⁻³]` reference air density at ~20 °C; corrected with `altitude` if provided.
- `type_ventilation`: `"temp_wind"` (ISO airing) or `"occupancy"` (area-based volumetric rule).
- `flowrate_person` `[L·s⁻¹·m⁻²]` used only in `"occupancy"` branch.

#### Physics

**Step A — Effective opening height (stack path)**  
For each transparent surface:
- parapet height \(h_p\) `[m]`,  
- window height \(h_w\) `[m]`,  
- **path height** (vertical center): \(h_{path,i} = h_p + \frac{h_w}{2}\),
- **fa height**: \(h_{fa,i} = \frac{h_w}{2}\).

The **useful stack height**:

\[
h_{w,st} = \max_i\!\left(h_{path,i} + \frac{h_{fa,i}}{2}\right) - \min_i\!\left(h_{path,i} - \frac{h_{fa,i}}{2}\right)
\tag{4.1}
\]

**Step B — Density correction**  
If `altitude` present, a standard atmosphere relation updates \(\rho_{a,ref}\). Outdoor density:

\[
\rho_{a,e} = \rho_{a,ref}\,\frac{291.15}{273.15 + T_e}
\tag{4.2}
\]

**Step C — Effective openable area**  

For each window \(i\), geometric area \(A_{w,i} = h_{w,i}\,w_i\).  
Open area \(A_{w,i}^{open} = A_{w,i}\,R_{w,i}\) with \(R_{w,i}\in[0,1]\).
If `Rw_arg_i` is missing or length mismatches the number of windows, default \(R_{w,i}=0.9\).

\[
A_{w,tot} = \sum_i A_{w,i}^{open}
\tag{4.3}
\]

**Step D — Airing volumetric flow (single-sided)**  

Using ISO 16798-7 §6.4.3.5.4:

\[
q_v = 3600\;\frac{\rho_{a,ref}}{\rho_{a,e}}\;\frac{A_{w,tot}}{2}\,
\left[\max\!\Big(C_{wnd}\,u_{site}^2,\; C_{st}\,h_{w,st}\,\lvert T_z-T_e\rvert\Big)\right]^{1/2}
\quad [\text{m}^3/\text{h}]
\tag{4.4}
\]

**Step E — Ventilation conductance**

\[
H_{ve} = \frac{c_{air}\,\rho_{air}}{3600}\;q_v
\quad [\text{W·K}^{-1}]
\tag{4.5}
\]

**Occupancy branch**: area-based simplified rule (constant per hour)

\[
H_{ve} = A_{use}\cdot (3.6\,\dot v_{pers})\cdot \frac{c_{air}\,\rho_{air}}{3600}
\tag{4.6}
\]

with \(\dot v_{pers}\) in `[L·s⁻¹·m⁻²]` and `3.6` converting L·s⁻¹·m⁻² to m³·h⁻¹·m⁻².

#### Outputs
- `np.ndarray` of `H_ve_k_t` `[W·K⁻¹]` (scalar or time-series depending on inputs).

#### Algorithm (pseudo)

```python
if type_ventilation == "temp_wind":
    extract all windows -> {height, width, parapet}
    compute hw_path_i, hw_fa_i -> hw_st  # Eq. (4.1)
    density correction -> rho_a_e        # Eq. (4.2)
    aw_tot -> Eq. (4.3)
    qv -> Eq. (4.4)
    Hve -> Eq. (4.5)
else:  # occupancy
    A_use <- building_object["building"]["net_floor_area"]
    Hve  <- Eq. (4.6)
return np.array(Hve)
```

#### Edge Cases & Validation
- No transparent surfaces → \(A_{w,tot}=0\) → \(H_{ve}=0\).
- `Rw_arg_i` length mismatch → warning + default 0.9.
- Negative or null `u_site` accepted; `max(·)` ensures stack/wind pick the dominant driver.

---

Function:`internal_gains(...)`  
---

**Physical purpose**: compute **internal sensible gains** \(\Phi_{int}\) `[W]` in the **thermally conditioned zone**, possibly accounting for **spillover** to adjacent unconditioned zones.

#### Signature

```python
def internal_gains(
    cls, building_type_class, a_use, unconditioned_zones_nearby=False,
    list_adj_zones=None, Fztc_ztu_m: float=1, b_ztu: float=1,
    h_occup: float=1, h_app: float=1, h_light: float=1, h_dhw: float=1,
    h_hvac: float=1, h_proc: float=1
) -> float:
```

#### Inputs (main)

- `building_type_class`: key for the lookup table `internal_gains_occupants` (imported from `source.table_iso_16798_1`).
- `a_use` `[m²]`: useful area of the **conditioned** zone.
- `h_*` `[-]`: hourly multipliers (profiles) for each sub-component (currently **occupants** and **appliances** are used).
- Coupling params for unconditioned zones:
    - `b_ztu` `[-]`: **adjustment factor** of the adjacent unconditioned zone (see §4.4, Eq. (4.13)).
    - `Fztc_ztu_m` `[-]`: **fractional path factor** conditioned→unconditioned in month `m` (lumped path coefficient).
    - `list_adj_zones`: **number** of adjacent zones (note: the current signature expects an **int**; see note below).

> **Note**: The code uses `for zones in range(list_adj_zones)` — pass an `int`. If a list is desired in the future, change to `for z in list_adj_zones:`.

#### Physics
Let \(q_{occ}\) and \(q_{app}\) be the nominal **density** of internal gains `[W·m⁻²]` for occupants/equipment per `building_type_class`.

**Base internal gains** in the **conditioned zone**:

\[
\Phi_{int,z}(t) = \big(q_{occ}\,h_{occup}(t) + q_{app}\,h_{app}(t)\big)\;A_{use}
\tag{4.7}
\]

**Optional spillover** to **unconditioned** adjacent zones (`unconditioned_zones_nearby = True`):  
The code currently **adds** a further term per adjacent zone combining a **direct duplicated** contribution and a **fractional transfer** modulated by \((1-b_{ztu})\,F_{ztc{\text -}ztu,m}\):

\[
\Phi_{int,z}^{eff}(t)
= \Phi_{int,z}(t) + \sum_{j=1}^{N_{adj}}
\left[\Phi_{int,z}(t) + \big(1-b_{ztu}\big)\,F_{ztc{\text -}ztu,m}\,\Phi_{int,z}(t)\right]
\tag{4.8}
\]


#### Output
- `float` `[W]` — instantaneous internal sensible gains for the conditioned zone with the current coupling rule.

#### Algorithm (pseudo)

```python
q_occ = internal_gains_occupants[building_type_class]['occupants']
q_app = internal_gains_occupants[building_type_class]['appliances']
Phi_base = (q_occ*h_occup + q_app*h_app) * a_use        # Eq. (4.7)
if unconditioned_zones_nearby:
    Phi_eff = Phi_base
    for _ in range(list_adj_zones):
        Phi_eff += Phi_base + (1-b_ztu)*Fztc_ztu_m * Phi_base
    return float(Phi_eff)
else:
    return float(Phi_base)
```
---

Function: `transmission_heat_transfer_coefficient_ISO13789(...)`  
---
**Physical purpose**: compute **transmission coupling** between a **thermally conditioned** zone (ztc) and **adjacent unconditioned** zone(s) (ztu) per ISO 13789, including the **ventilation of the unconditioned** zone to the outside.

> **Important**: In the snippet, `building_object`, `orient_all_zones`, and `volume_all_zones` are referenced but **not passed**. In practice you should pass the **adjacent zone object** (or the whole `BUI`) and extract what you need locally. The equations below describe the intended physics.

#### Signature (as provided)
```python
def transmission_heat_transfer_coefficient_ISO13789(adj_zone, n_ue=0.5, qui=0):
    ...
    return H_ztu_tot, b_ztu_m
```

#### Concepts & Notation
- \(H_{tr}\) is decomposed as:

\[
H_{tr} = H_d + H_g + H_u + H_a
\tag{4.9}
\]

with:
- \(H_d\): direct envelope transmission to **exterior**,
- \(H_g\): ground transmission,
- \(H_u\): via **unconditioned** space,
- \(H_a\): to **adjacent buildings** (not used here).

#### Step 1 — Transmission **conditioned → unconditioned**
For the **interface** between ztc and ztu:

\[
H_{d,zt{\text -}ztu} = \sum_{k \in\mathcal{E}_{zt{\text -}ztu}} U_k\,A_k
\tag{4.10}
\]

where the set \(\mathcal{E}_{zt{\text -}ztu}\) are elements on the **shared** boundary.

#### Step 2 — Transmission **unconditioned → exterior**

For ztu walls not shared with ztc (i.e., exposed or to other media):

\[
H_{d,ztu{\text -}ext} = \sum_{k \in\mathcal{E}_{ztu{\text -}ext}} U_k\,A_k
\tag{4.11}
\]

#### Step 3 — **Ventilation** of unconditioned zone
ISO 13789 suggests using **air change rate** \(n_{ue}\) `[h⁻¹]` for ztu → outside.  

Let \(V_u\) `[m³]` be ztu air volume. Define:

\[
q_{ue} = V_u\,n_{ue} \quad [\text{m}^3/\text{h}], \qquad
q_{iu} = q_{i\to u} \quad [\text{m}^3/\text{h}] \text{ (often set to 0 to avoid overestimation)}
\tag{4.12a}
\]

Use the standard \(\rho c\) factor \(\approx 0.33\) `[Wh·m⁻³·K⁻¹]` for flows expressed in m³·h⁻¹:

\[
H_{ve,ue} = 0.33\,q_{ue}, \qquad H_{ve,iu} = 0.33\,q_{iu}
\tag{4.12b}
\]

By **default** in the code: \(q_{iu} = 0\).

#### Step 4 — Aggregate coupling terms
\[
H_{ue} = H_{d,ztu{\text -}ext} + H_{ve,ue}, \qquad
H_{iu} = H_{d,zt{\text -}ztu} + H_{ve,iu}
\tag{4.12c}
\]

Total **ztu coupling**:

\[
H_{ztu,tot} = H_{iu} + H_{ue}
\tag{4.12d}
\]

**Adjustment factor** \(b_{ztu,m}\) (ISO 13789 monthly convention):

\[
b_{ztu,m} = \frac{H_{ue}}{H_{ue} + H_{iu}} = \frac{H_{ue}}{H_{ztu,tot}}
\tag{4.13}
\]

\(b_{ztu,m}\in[0,1]\) measures how much the unconditioned zone is “anchored” to the **outside** rather than to the **conditioned** neighbor.

#### Output
- `H_ztu_tot` `[W·K⁻¹]` — total coupling of the unconditioned zone.
- `b_ztu_m` `[-]` — monthly factor (in the current code computed once from static inputs).

#### Practical extraction with your `BUI` structure

- For **a given unconditioned zone** `adj_i`:
    - Build sets:
        - \(\mathcal{E}_{zt{\text -}ztu}\): elements in `adj_i` whose `orientation_elements` **match** the interface direction to the conditioned zone (your code uses equality tests by `NV/SV/EV/WV/HOR`).
        - \(\mathcal{E}_{ztu{\text -}ext}\): elements in `adj_i` **not** on the interface.
    - Use `adj_i.volume` → \(V_u\).  
    - Pick `n_ue` from `df_n_ue` by air-tightness class or keep default `0.5 h⁻¹`.

#### Algorithm (pseudo; robust version)

```python
def transmission_heat_transfer_coefficient_ISO13789(BUI, adj_zone_name, n_ue=0.5, qui=0):
    adj = get_adj_zone(BUI, adj_zone_name)
    A = np.asarray(adj["area_facade_elements"], dtype=float)
    U = np.asarray(adj["transmittance_U_elements"], dtype=float)
    ORI = np.asarray(adj["orientation_elements"])
    # Define which orientations correspond to zt-ztu interface (project specific rule):
    mask_interface = is_interface_to_conditioned_zone(ORI, adj, BUI)   # boolean mask
    Hd_zt_ztu  = float(np.sum(A[mask_interface] * U[mask_interface]))   # Eq. (4.10)
    Hd_ztu_ext = float(np.sum(A[~mask_interface] * U[~mask_interface])) # Eq. (4.11)

    # Ventilation terms (Eq. 4.12)
    Vu = float(adj["volume"])
    que = Vu * n_ue
    Hve_ue = 0.33 * que
    Hve_iu = 0.33 * float(qui)

    Hue = Hd_ztu_ext + Hve_ue
    Hiu = Hd_zt_ztu + Hve_iu
    Hztu_tot = Hue + Hiu                                 # Eq. (4.12d)
    b_ztu_m  = Hue / Hztu_tot if Hztu_tot > 0 else 1.0   # Eq. (4.13)
    return float(Hztu_tot), float(b_ztu_m)
```

#### Edge Cases
- If `A`/`U` vectors contain **dtype=object** (as in your snippet), cast explicitly to `float`.
- If `Hztu_tot = 0` (degenerate geometry), define `b_ztu_m = 1.0` by convention (fully outdoor-anchored).

---

## Integration Roadmap (Future Enhancements)

- **Air leaks**: integrate infiltration losses for cracks and envelope leakage tests.
- **Cross ventilation**: include simultaneous airflow paths between opposite façades.
- **Mechanical ventilation**: handle forced air systems with user‑defined flow rates and recovery efficiency.

---

## References

- **ISO 52016‑1:2017**, § 6.5.10 Ventilation and Heat Transfer Coefficients  
- **ISO 16798‑7:2017**, § 6.4.3.5 Natural Ventilation Airflow  
- **ISO 16798‑1:2019**, § M1–M10 Internal Gains  
- **ISO 13789:2017**, § 7 Transmission Heat Transfer Coefficients through Adjacent Spaces

