## <h1 style="color:#df1b12; margin-bottom:0px; font-weight:bold"><strong>Overall procedure - Energy Need EN ISO 52016</strong></h1>


```python
@classmethod
def Temperature_and_Energy_needs_calculation(
    cls,
    building_object,
    nrHCmodes=2,
    c_int_per_A_us=10000,
    f_int_c=0.4,
    f_sol_c=0.1,
    f_H_c=1,
    f_C_c=1,
    delta_Theta_er=11,
    **kwargs,   # weather_source='pvgis' | 'epw', path_weather_file=... (when epw)
)
```

This guide explains how the `Temperature_and_Energy_needs_calculation(...)` classmethod computes hourly **operative temperatures** and **heating/cooling needs** following **ISO 52016:2017**. 
It walks through inputs, preprocessing, per‑timestep assembly of the linear system, HVAC setpoint logic, numerical safeguards, and outputs.

---

## Inputs

### Building description (`building_object`)
- `building.net_floor_area` (m²)
- `building_parameters.temperature_setpoints`
  - `heating_setpoint`, `heating_setback`, `cooling_setpoint`, `cooling_setback` (°C)
- `building_parameters.system_capacities`
  - `heating_capacity` (W), `cooling_capacity` (W)
- `building_surface`: list of surfaces with fields (examples)
  - `type`: `"opaque" | "transparent" | "adiabatic" | "adjacent" | "ground"`
  - `area` (m²), `u_value` (W/m²K) (if relevant), `thermal_capacity` (J/K) (optional)
  - `orientation = { azimuth, tilt }` with sky view factor `sky_view_factor ∈ [0,1]`
  - windows: `g_value`, shading info (optional)
- optional **adjacent zones** block for coupling to unconditioned zones.

### Model parameters (function arguments)
- `nrHCmodes` — modes evaluated: 1=free, 2=H or C, 3=both (default 2).
- `c_int_per_A_us` — areal internal capacity (J/m²K) → multiplied by `net_floor_area` to get `C_int`.
- `f_int_c`, `f_sol_c` — convective fractions for **internal** and **solar** gains.
- `f_H_c`, `f_C_c` — convective fractions for **heating** and **cooling** system emission.
- `delta_Theta_er` — ΔT external air–sky (°C) for radiative exchange on external surfaces.
- `kwargs`: weather provider (`"pvgis"` or `"epw"`, with `path_weather_file` for EPW).

---


### Purpose

**Purpose**: Solve the **zone energy balance** hour by hour:

\[
\underbrace{\mathbf{A}}_{\text{conduction + convection + radiation + capacities}} 
\cdot 
\underbrace{\mathbf{X}}_{\text{node temps}}
=
\underbrace{\mathbf{B}}_{\text{weather + gains + HVAC}}
\]

- `X` contains the unknown temperatures at the **air node** (zone) and the **conduction nodes** for each surface.
- The solution is computed for up to **three columns**: free-floating, heating-upper, cooling-upper.


---

## 1) Weather & timebase

1. Choose weather source:
    - `"pvgis"` → provider called without a file path.
    - `"epw"` → pass `path_weather_file` when provided.
2. Obtain `simulation_df` with hourly columns, e.g.:
    - `T2m` (external temperature), global/direct/diffuse irradiance per orientation (`I_sol_tot_*`, `I_sol_dir_w_*`, `I_sol_dif_*`), wind speed, etc.
3. `Tstepn = len(simulation_df)` — total hours simulated.
4. Define `Dtime = 3600 s` for each hour (1‑hour step).

---

## 2) Surface hydration, classification, and aggregation

1. **Classify** each surface:
    - `"GR"`: ground (opaque with `sky_view_factor == 0`)
    - `"AD"`: adiabatic
    - `"ADJ"`: adjacent (opaque to unconditioned zone)
    - `"W"`: transparent (window)
    - `"EXT"`: other external opaque
2. **Orientation string**:
    - tilt 0 → `"HOR"`, tilt 90 → `"NV" | "EV" | "SV" | "WV"` based on azimuth, else heuristic (`HOR` for shallow tilts).
3. **Hydrate coefficients** if missing (typical defaults):
    - internal convection `h_ci` (facade/roof/ground/adiabatic)
    - external convection `h_ce`
    - internal & external radiation `h_re`
4. **Windows**: collect `g_value` per surface (0 for non‑windows).
5. **Areas**: build `area_elements` and total `area_elements_tot`.
6. **Aggregate** by direction (optional internal step) to simplify the system, then **rebuild arrays** (types, orientations, `h_ci`, `h_ce`, `h_ri`, `h_re`, areas, `g_value`, `sky_view_factor`).

---

## 3) Zone state & node topology

1. **Node graph** (`Number_of_nodes_element`):
    - Node index `0` → **zone air/furniture**.
    - For each surface `eli` with `Pli` conduction nodes, the **last** node (`Pli-1`) is the **internal surface node**.
    - Arrays: `Rn` (# of nodes), `Pln` (nodes per surface), `PlnSum` (overall number of nodes for all surfaces).
2. **Capacities**:
    - Zone capacity `C_int = c_int_per_A_us × net_floor_area`.
    - Lump **adiabatic** surface capacities into `C_int` (robustness).
    - Per-surface areal capacities from `Areal_heat_capacity_of_element` → mapped into `C_state` at the corresponding node indices.
3. **Conductances**:
    - From `Conduttance_node_of_element` (array `h_pli_eli`) for intra‑element conduction links.
4. **Radiative mean**:
    - Internal mean radiative heat transfer coefficient (area‑weighted).

---

## 4) Ground, thermal bridges, and solar preparatory data

1. **Ground** model: `Temp_calculation_of_ground(building_object)` returns:
    - monthly ground temperature `Theta_gr_ve[1..12]`
    - equivalent resistance `R_gr_ve`
    - (and thermal bridge term `thermal_bridge_heat` if included in that structure).
2. **Solar absorption**:
    - `Solar_absorption_of_element` → `a_sol_pli_eli` for outer nodes, and window transmission with `g_value`.
3. **Shading**:
    - Frame fraction `F_fr` (default 0.25 if unknown) reduces transparent area; optional obstacle factors per window column.

---

## 5) Internal and ventilation gains & profiles

1. Build hourly **profiles**:
    - `occupancy_profile`, `appliances_profile`, `lighting_profile`
    - `heating_profile`, `cooling_profile`, `ventilation_profile`
2. **Fallbacks**: if any **H/C/ventilation** profile is empty (all zero), **use occupancy** as a proxy to avoid a perpetually off system.
3. Compute **ventilation heat transfer** `H_ve` each hour (function of outdoor T, wind, and profile).
4. Compute **internal gains** (W) from building use and profiles.  
    Split convective vs radiative using `f_int_c`:
    - Convective part to **air node**
    - Radiative part to **internal surface nodes** (area‑weighted)

---

## 6) Adjacent (unconditioned) zones (if any)

1. If `adj_zones_present`:
    - Use ISO 13789 to calculate the transmission (`H_ztu`, `b_ztu`, `F_ztc_ztu_m`) per adjacent zone.
    - Propagate an **effective** adjacent zone temperature `θ_ztu(t)` each hour using:
        - previous indoor operative temperature,
        - outdoor temperature,
        - internal/solar gains in the unconditioned space,
        - a growth limiter `c_ztu_h_max` (from tabulated guidance).
2. For **ADJ** surfaces, use `θ_ztu(t)` as the **external boundary** in the matrix assembly.

---

## 7) Per‑timestep assembly (ISO 52016 equations)

At each hour **t**, assemble the system for up to **3 columns** (free, heating-upper, cooling-upper):

### 7.1 Right‑hand side `B` contributions

For the **zone air node (row 0)**:

- **Capacitive carryover**: `(C_int / Δt) · θ_old_air`
- **Ventilation**: `H_ve · T_out(t)`
- **Thermal bridges**: `H_tb · T_out(t)` (from ground/bridges model)
- **Convective internal gains**: `f_int_c · Φ_int(t)`
- **Convective solar gains**: `f_sol_c · Φ_solar(t)`
- **Convective HVAC portion**: `f_H_c·Φ_H + f_C_c·Φ_C` *when the column represents an upper case with nonzero load*

For each **internal surface node**:

- **Radiative gains** assigned by area ratio: `(1 - f_int_c)·Φ_int + (1 - f_sol_c)·Φ_solar` divided by total internal area (W/m² basis)
- **Capacitive carryover** of that node: `(κ_pli,eli / Δt) · θ_old_node`

For each **external surface node**:

- **External convection+radiation** with outdoor air: `(h_ce + h_re) · T_out(t)`
- **Sky radiation** term: `- φ_sky = - (sky_factor · h_re · ΔT_er)`
- **Solar absorption** term for the outer node: `a_sol_pli_eli · I_sol_tot_orientation(t)`
- For **ADJ** surfaces, use `T_adj_zone(t)` instead of `T_out(t)`.
- For **GR** surfaces, use `(1/R_gr) · T_ground(month)`.

### 7.2 Matrix `A` contributions

- **Zone air row (0,0)**:
    - add `(C_int/Δt) + H_ve + H_tb + Σ (A_eli·h_ci_eli)`  
    - subtract `A_eli·h_ci_eli` towards each **internal surface node** (coupling)
- **Internal surface node**:
    - add own capacity term `(κ/Δt)`
    - add `h_ci_eli` (convective to air) and *radiative* coupling to all other internal surfaces via area‑weighted term:

        \[
        h_{ri,eli} \cdot \sum_k \left( \frac{A_k}{A_\text{int,tot}} \right)
        \]
    
    - subtract coupling to **air node**: `h_ci_eli`
    - subtract radiative couplings to other internal surfaces via area ratios
    - add **conduction** links `+h_{pli-1,eli}` to previous node and `+h_{pli,eli}` to next node; subtract the symmetric terms on neighbors
- **External surface node**:
    - add `(h_ce + h_re)` for **EXT/ADJ** or `(1/R_gr)` for **GR`
    - add own capacity term `(κ/Δt)`
    - add conduction links to next/previous node (as above)

> A small **diagonal regularization** is applied to keep `A` non‑singular.

---

## 8) Solve the system(s) and compute operative temperatures

1. Check rank/conditioning; regularize if needed.
2. Solve `A·X = B` for each column (free, heating-upper, cooling-upper).
3. Extract:
    - `θ_int_air(t)` = `X[air_row, :]`
    - `θ_int_r_mn(t)` = area‑weighted average of **internal surface node** temperatures
    - `θ_op(t)` = `0.5 · (θ_int_air + θ_int_r_mn)` for each column.

---

## 9) HVAC setpoint logic (ISO 52016 §6.5.5.2)

For each hour:

1. Determine **active setpoints** using `heating_profile`/`cooling_profile`:
    - no heating → use **heating setback**; if special sentinel (e.g., `< -995`), **disable heating**.
    - no cooling → use **cooling setback**; if `> +995`, **disable cooling**.

2. Compare **free** operative temperature `θ_op_free` with setpoints:
    - If `θ_op_free < θ_heat_set`: compute **heating** load using eq. (27):
    
    \[
    Φ_{HC} = Φ_{H,\text{max}} \cdot \frac{θ_\text{set} - θ_{op,0}}{θ_{op,H} - θ_{op,0}}
    \]
    
    where `θ_{op,H}` is the “upper” heating solution and clip to `heating_capacity`.
    
    - If `θ_op_free > θ_cool_set`: compute **cooling** load similarly (negative W), clip to `cooling_capacity`.

3. If capacity is **not** saturated (partial load), **reassemble** with the actual HVAC load and **resolve** once so that the achieved `θ_op` equals the setpoint (within tolerance).
4. Save `Φ_HC(t)` into the time series (`Q_HC`, positive for heating, negative for cooling) and record `θ_op_act(t)`.

---

## 10) Energy accounting (Sankey-style, optional)

Per hour, accumulate **Wh** contributions:

- **Inputs**: `Heating`, `Internal gains`, `Solar & free-gain`
- **Outputs**: `Cooling (extracted)`, `Ventilation`, `Thermal bridges`, `Ground`, `Transmission by surface`
- **Storage**: change in state energy (`∑ C_state · Δθ / 3600`)

At the end:

- Check balance: Inputs ≈ Outputs + Storage (absorb small residuals into Storage if <1% Inputs).

---

## 11) Build outputs

### 11.1 Hourly results (after warm‑up)
DataFrame columns:

- `Q_HC` (W) — signed HVAC need (+: heating, −: cooling)
- `T_op` (°C) — achieved operative temperature
- `T_ext` (°C) — outdoor temperature
- Convenience splits:
    - `Q_H = max(Q_HC, 0)`
    - `Q_C = max(-Q_HC, 0)`

### 11.2 Annual aggregation

- `Q_H_annual = Σ Q_H · Δt` (Wh)
- `Q_C_annual = Σ Q_C · Δt` (Wh)
- Per-area KPIs (Wh/m²): divide by `building.net_floor_area`.

---

## 12) Units & conventions

- Temperature `θ`: **°C**  
- Power `Φ` / `Q`: **W**  
- Energy: **Wh** (integration across hours)  
- Capacity `C`, `κ`: **J/K** (areal capacities multiplied by area become **J/K** at node)
- Conductances `h_*`: **W/m²K**; when multiplied by area → **W/K**.

---

## 13) Numerical stability & robustness

- **Diagonal regularization** of `A` (min diag value based on ∥A∥∞) to avoid singularities.
- **Warm‑up** (e.g., first month) simulated and typically **excluded** from reporting to reduce initial transients.
- Limiters for **adjacent-zone** temperature growth (`c_ztu_h_max`) and **ventilation** sanity checks (non-negative, finite).
- Clamp microscopic residuals (|x| < 1e‑9 → 0) in energy accounting.

---

## 14) Minimal checklist before running

- Weather source set correctly; EPW file path valid if used.
- Surfaces have: `type`, `area`, `orientation`, `sky_view_factor`, and suitable `U`/`g_value` where relevant.
- Setpoints and capacities are present and in **W**/**°C**.
- Profiles are present or fallbacks enabled.

---

## 15) Worked outline (pseudo‑algorithm)

```text
get weather(sim_df), Tstepn
classify & hydrate surfaces (types, orientation strings, h_ci/h_ce/h_ri/h_re, areas, g-values)
aggregate by direction (optional) → rebuild arrays

nodes = Number_of_nodes_element(building_object)
C_state[air] = c_int_per_A_us * net_floor_area (+ AD capacities)
C_state[elem nodes] from Areal_heat_capacity_of_element
precompute: ground model, thermal bridges, conductances h_pli_eli, solar absorption a_sol_pli_eli
build hourly profiles (H/C/vent/occ/app/light) with fallbacks

for each hour t:
  assemble A, B for (free, heat-upper, cool-upper):
    zone row: capacities, H_ve, H_tb, convective gains + HVAC convective chunk
    internal nodes: capacities, conduction, convection to air, radiative coupling, gains (radiative chunks)
    external nodes: capacities, boundary to outdoor/adj/ground, solar terms
  solve → X (three columns)
  compute T_op for each column
  apply setpoint logic (eq. 27), clip to capacities, possibly reassemble with partial Φ_HC
  write Q_HC(t), T_op_act(t)
  accumulate energy terms (inputs/outputs/storage)

post:
  build hourly DataFrame (drop warm-up)
  integrate Wh → annual totals and Wh/m²
  return hourly_results, annual_results_df
```

---

## 16) Interpretation tips

- `Q_HC` is **need**, not system energy use. Apply system efficiencies (e.g., seasonal COP/η) downstream to obtain **consumption**.
- If `T_op` frequently deviates from setpoints, the **capacity** is insufficient or profiles/weather are too demanding.
- Large **storage** swings indicate high thermal mass; near-zero annual storage is expected (balance closure).

---

## 17) Common pitfalls & remedies

- **All-zero profiles** → no HVAC action: enable fallbacks or fix schedules.
- **Missing g-values** → underestimated solar gains for windows: add `g_value`.
- **Incorrect sky view factor** → radiative cooling to sky misrepresented: ensure `0..1`.
- **Singular matrix** → add/verify capacities, check AD nodes, keep time step at 1h, allow diagonal regularization.
- **Units confusion** → check W vs Wh vs J/K; capacities are often mistaken for J/m²K without conversion.

---

!!!Note

    *This document describes the computational steps implemented by the method and their physical meaning, aligned with ISO 52016 methodology (free-floating, upper-limit solutions, and setpoint-based interpolation with capacity clipping).*

    *This library was developed to showcase specific computational elements outlined in the relevant technical standards. It is designed to supplement, not replace, the official regulations, as these are crucial for understanding the underlying calculations. Intended for demonstration and testing purposes only, this library is distributed as open source without protections against misuse or misapplication.*

    *The opinions and information contained in this document belong to the authors and do not necessarily represent the official stance of the European Union. Neither the European Union's institutions and bodies, nor anyone acting on their behalf, shall bear responsibility for how the information herein is utilized.*



