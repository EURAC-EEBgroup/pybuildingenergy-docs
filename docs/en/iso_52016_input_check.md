<h1 style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #df1b12;">ISO 52016 Input Check</h1>


The data provided before being used for the simulation are processed and evaluated to be considered fit for the simulation. This process includes a series of checks that allow to identify any potential errors. 
The following controls are applied:

---
## <h2 style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #df1b12;">Direction from orientation</h2>


**Function Name**:
`_dir_from_orientation(azimut:float, tilt:float) -> str`

**Purpose**: 
This function mapd the orientation of the surface (azimuth and tilt) and returns the direction of the surface.

**Return**
One of: `HOR` (horizontal), `NV`,`EV`, `SV`, `WV`(vertical faces; North, East, South, West) 

**Validations & rules**
- Tilt checks
    - If `tilt == 0` (|Δ| ≤ 1e-9): return `"HOR"`.
    - If `tilt != 90` (|Δ| > 1e-6): uses a fallback threshold:
        - `tilt < 45 → "HOR"`
        - `tilt ≥ 45 → "NV"` (treat as a generic vertical).

- Azimuth checks (only when considered vertical):
    - Normalize `azimuth % 360`.
    - Exact snaps (|Δ| ≤ 1e-6):
        - `0` or `360` → `"NV"`, `90` → `"EV"`, `180` → `"SV"`, `270` → `"WV"`.
    - Otherwise: snap to the nearest of `[0,90,180,270]`.

**Notes**

This function does not emit messages; it enforces interpretation by thresholds/snaps.

---
## <h2 style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #df1b12;">Opaque facade areas in adjacent zone</h2>

**Function Name**: `_adj_op_area_in_dir(adj_zone: dict, dir_code: str) -> float`

**Purpose**: 
Compute the sum of opaque (“OP”) facade areas in `adj_zone` for the given direction code `("NV"|"EV"|"SV"|"WV")`.

**Validations & rules**

- Upper-cases and matches:
    - `typology_elements == "OP"` and 
    - `orientation_elements == dir_code`

- If no match: returns `0.0`.

**Notes**

No messages; pure filtering/aggregation with safe default `0.0`.

---
## <h2 style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #df1b12;">Check heating system inputs</h2>

**Function Name**: `check_heating_system_inputs(system_input: dict) -> dict`

**Purpose**: 
Load and **validate** heating system configuration, selecting the correct **TB14** table and ensuring compatible fields for generator control logic
Example of **TB14**:

```python
TB14 = pd.DataFrame({
    "Emitters_nominale_deltaTeta_air_C": [50, 15, 25],
    "Emitters_exponent_n": [1.3, 1.1, 1.0],
    "Emitters_nominal_deltaTeta_Water_C": [20, 5, 10],
}, index=["Radiator", "Floor heating", "Fan coil"])
```

**Returns**

```python
{
  "TB14_used": pd.DataFrame,   # custom or default TB14
  "emitter_type": str,         # validated (possibly auto-adjusted)
  "messages": list[str],       # human-readable validations/fixes
  "config": dict               # normalized config (may include auto-fixes)
}
```

**Validations & auto-fix logic**

1) **TB14 selection**

   - If `system_input["TB14"]` is a` pd.DataFrame` → use it.
      - Message: `Custom TB14 table loaded from input`.
   - Else → fallback to `TB14_backup`.
      - Message: `Default TB14 table loaded from global_inputs.py`.

2) **`emitter_type` presence in TB14 index**

   - If missing from `TB14.index` → *auto-set* to the *first available index* (or `None` if empty).
      - Message: `Emitter type '...' not found ... auto-set to '...'.`
   - Else → keep as is.
      - Message: `Emitter type '...' found in TB14.`

3) **`gen_flow_temp_control_type` validation**
   - Allowed: `"Type A" | "Type B" | "Type C".`
   - *Type A* requires `gen_outdoor_temp_data` as `pd.DataFrame`:
      - If not a DataFrame → *auto-switch to "Type B"*.
         - Message: `For 'Type A' ... must be provided ... → switched to 'Type B'.`
      - Else → `'gen_outdoor_temp_data' provided ...`.
   - *Type C* requires numeric `θHW_gen_flw_const`:
      - If missing/None → auto-set to `50.0`.
      - Message: `⚠️ 'θHW_gen_flw_const' not provided ...; setting it to 50.`
   - Any other value →* auto-set to "Type B"*.
      - Message: `⚠️ Invalid value ... Setting to 'Type B'.`

**Side effects**
Returns a normalized copy of the input config in "config"; original dict is not mutated by the function.

---

## <h2 style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #df1b12;">Validation and optional sanitation of a BUI structure</h2>

**Function Name**: `sanitize_and_validate_BUI(bui: dict, fix: bool = True, eps: float = 1e-6, defaults: dict | None = None) -> tuple[dict, list[dict]]`

**Purpose**: 
Deep validation and optional sanitation of a BUI structure (building, surfaces, adjacent zones, and their pairing). It can also re-balance areas and split surfaces to maintain geometric/physical consistency.
There are 4 main controls:
- **Building-level checks**
- **Surface-level checks**
- **Adjacent zone checks**
- **Adjacency pairing, window caps & residual splitting**

**Returns**

   - `bui_clean`: deep-copied and possibly corrected BUI.
   - `issues`: list of structured messages:

```python
{"level": "ERROR|WARN|INFO",
 "path": "dot.notation or index path",
 "msg": "human-readable message",
 "fix_applied": bool}
```

**Defaults used when `defaults` is None**

```python
{
  "opaque_u_default": 0.5,
  "transparent_u_default": 1.6,
  "g_default": 0.6
}
```

#### 1) **Building-level checks**

- Keys: `net_floor_area`, `exposed_perimeter`, `height`

   - Must be numeric and > 0.
   - If `fix` and value is exactly `0` → set to `max(eps, 1.0)` (⚠️ `WARN` with fix).
   - Else → `ERROR`.

- `n_floors`

   - Must be numeric and > 0.
   - If `fix` and value is exactly `0` → set to `1` (⚠️ `WARN` with fix).
   - Else → `ERROR`.

#### 2) **Surface-level checks (`building_surface[*]`)**

- **Type typos** auto-corrected (`"opque"|"opaqu"|"trasparent"` → `"opaque"|"transparent"`) with `WARN`.
- `type` must be in {`"opaque"`, `"transparent"`, `"adiabatic"`, `"adjacent"`} → else `ERROR`.
- `area` must be numeric > 0.
   - If `fix` and `area` is exactly `0` → set to `max(eps, 1.0)` (⚠️ `WARN` with fix).
   - Else → `ERROR`.
- `sky_view_factor` must be in [0.0, 1.0].
   - If `fix` and numeric → **clipped** into range (⚠️ `WARN`).
   - Else → `WARN`.

- **Thermal properties**
   - For `opaque/transparent`: `u_value` > 0.
      - If invalid and `fix` → set to default (opaque_u_default or transparent_u_default) (⚠️ `WARN`).
      - Else → `ERROR`.
   - For `transparent`: `g_value` > 0.
      - If invalid and `fix` → set to default (g_default) (⚠️ `WARN`).
      - Else → `ERROR`.

- **Transparent dimensions**
   - `height > 0`, `width > 0.`
      - If invalid and `fix` → set both to `1.0` (⚠️ `WARN`).
      - Else → `ERROR`.
   - `parapet` must be in `[0, height]` when both numeric.
      - If out of range and `fix` → clamp to `[0, height]` (⚠️ `WARN`).
      - Else → `WARN`.

- **Orientation recommendations**
   - `tilt` recommended in {0, 90}.
      - If numeric non-standard and `fix` → normalize to nearest of {0, 90} (⚠️ `WARN`).
      - Else → `WARN`.
   - `azimuth` recommended in {0, 90, 180, 270}.
      - If numeric non-standard and `fix` → snap to nearest multiple of 90 (⚠️ `WARN`).
      - Else → `WARN`.

#### 3) **Adjacent zones checks (adjacent_zones[*])**

- `volume > 0.`
   - If invalid and `fix` → set to `1.0` (⚠️ `WARN`).
   - Else → `ERROR`.

- **Array length coherence** across:
   - `area_facade_elements, typology_elements, transmittance_U_elements, orientation_elements.`
      - If lengths mismatch → `ERROR`.

- `transmittance_U_elements` must be > 0:
   - If invalid and `fix` → set invalid entries to `opaque_u_default` (⚠️ `WARN`).
   - Else → `ERROR`.

#### 4) **Adjacency pairing, window caps & residual splitting**

This stage ensures geometric consistency between:

- BUI vertical **adjacent** surfaces,
- the **opaque** (“OP”) areas declared in the **adjacent zone** on the **same cardinal direction**, and
- the **transparent** (windows) areas on the same direction.

It operates in two passes (an inner while-loop and a later full pass), using the helpers:

- `_azimuth_to_dir:` snap 0/90/180/270 →` "NV"|"EV"|"SV"|"WV"`, else `None`.
- `_dir_from_orientation:` more general mapper used later.

**4.1 For each vertical** `building_surface` **of type** `"adjacent"` **with** `name_adj_zone`:

- Compute:  
   - `A_bui_orig`: area of the adjacent BUI surface.
   - `A_adj_dir_cap`: sum of **adjacent zone OP areas** in the same direction.

- **Cap OP area to BUI area**:

   - If `A_adj_dir_cap > A_bui_orig + eps`:

      - If `fix`: scale down those OP areas proportionally (⚠️ WARN with scale factor).
      - Else: ERROR.

**Window check on same direction**

   - Compute `A_win_dir` = sum of *all vertical transparent* surfaces in the same direction.
   - Compute `diff = max(A_bui_orig - A_adj_dir_cap, 0).`
   - If `A_win_dir > diff + eps`:
      - If `fix`: **scale all those windows** proportionally to sum to diff (⚠️ WARN with window scale factor).
      - Else: `ERROR`.

**Residual exterior creation**

   - `diff_ext = max(A_bui_orig - A_adj_dir_cap, 0).`
   - If `diff_ext > eps`:
      - If `fix`:
         - **Append** a new `"opaque"` surface with area `diff_ext` (same orientation, external),
         - **Shrink** the `"adjacent" `surface area to `A_adj_dir_cap`.
         - ⚠️ `WARN` describing creation and resizing.
      - Else: `ERROR` (unallocated residual).

**4.2 Final pass: split all `"adjacent"` verticals (consistency sweep)**

- For each `"adjacent"` vertical surface:

   - Compute direction via `_dir_from_orientation`.
   - Fetch matching adjacent zone and compute `A_adj_dir` via `_adj_op_area_in_dir.`
   - Cap `A_adj_dir` to `A_bui` with `WARN` if it exceeds.
   - If `diff = A_bui - A_adj_dir > 1e-9`:
      - Shrink the "adjacent" area to A_adj_dir.

---
## <h2 style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #df1b12;">Thermal and Adjacent Zone</h2>

Uno degli errori più caratteristici può essere quello di immetere dei valori errati di superficie della parete di confine tra la zona termica e la zona non termica. Un esempio è quello di dare dei valori più alti della superificie della parete nella zona non termica rispetto alla superificie della parete nella zona termica. In questo caso se il controllo risulta essere negativo allora il tool imposta il valore del superificie della zona non termica uguale a quello della zona termica. 
Qui voglio dire che sebbene la superficie di contatto è la stessa pu`o succedere che la parete della zona termica sia o totlamente a contatto con la zon non termica o solamente una parte a contatto con la zona termica   


## <h2 style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #df1b12;">Quality check of system input `check_heating_system_inputs`</h2>


This function validates and normalizes the input configuration for the heating system. It performs the following checks:

1. **TB14 Table**: 
   - If a custom `TB14` DataFrame is provided, it is used.
   - Otherwise, the default `TB14` from `global_inputs.py` is used.

2. **Emitter Type Validation**:
   - If the `emitter_type` is not found in the selected `TB14` table, it is automatically set to the first available emitter type, and a warning message is generated.

3. **Generator Flow Temperature Control Type (`gen_flow_temp_control_type`)**:
   - **Type A**: Requires `gen_outdoor_temp_data` as a DataFrame. If not provided, it switches to `Type B` and generates a warning.
   - **Type C**: If `θHW_gen_flw_const` is not provided, it defaults to `50` and a warning is shown.
   - **Invalid Control Type**: Any other values are automatically set to `Type B`.

The function returns:
- The selected `TB14` table.
- The validated `emitter_type`.
- A list of messages about any changes or validations.
- The normalized input configuration.

