
# INPUT_SYSTEM_HVAC — Reference & Setup Guide

This document explains every field in the `INPUT_SYSTEM_HVAC` configuration used by the heating system model (emitter → distribution → generator). It also shows how to customize control curves and upload your own emitter tables.

> **Scope**: space-heating only (cooling is ignored here). All powers are thermal unless stated otherwise.

---

## 1) High-level structure

```python
INPUT_SYSTEM_HVAC = {
  # Emitter (room-side heat emission)
  "emitter_type": ...,
  "nominal_power": ...,
  "emission_efficiency": ...,
  "flow_temp_control_type": ...,
  "selected_emm_cont_circuit": ...,
  "mixing_valve": ...,
  # (Optional) custom emitter tables
  # "TB14": ...,
  # "heat_emission_data": pd.DataFrame(...),
  "mixing_valve_delta": ...,
  # "constant_flow_temp": ...,

  # Distribution (piping, auxiliaries)
  "heat_losses_recovered": ...,
  "distribution_loss_recovery": ...,
  "simplified_approach": ...,
  "distribution_aux_recovery": ...,
  "distribution_aux_power": ...,
  "distribution_loss_coeff": ...,
  "distribution_operation_time": ...,

  # Generator (boiler/HP/plant loop)
  "full_load_power": ...,
  "max_monthly_load_factor": ...,
  "tH_gen_i_ON": ...,
  "auxiliary_power_generator": ...,
  "fraction_of_auxiliary_power_generator": ...,
  "generator_circuit": ...,

  # Generator flow-temperature control
  "gen_flow_temp_control_type": ...,
  "gen_outdoor_temp_data": pd.DataFrame(...),

  "speed_control_generator_pump": ...,
  "generator_nominal_deltaT": ...,
  "mixing_valve_delta": ...,

  # Optional explicit generator setpoints
  # "θHW_gen_flw_set": ...,
  # "θHW_gen_ret_set": ...,

  # Efficiency model
  "efficiency_model": ...,

  # Calculation options
  "calc_when_QH_positive_only": ...,
  "off_compute_mode": ...,
}
```

---

## 2) Emitter block (room-side heat delivery)

| Field | Type | Example | Meaning |
|---|---|---|---|
| `emitter_type` | `str` | `"Floor heating 1"` | Emitter family/preset. Used to pick default emission characteristics. |
| `nominal_power` | `float` | `8` | Nominal emitter power (kW thermal). Used for checks and backstops in emission calc. |
| `emission_efficiency` | `float` | `90` | Emission efficiency in **%** (heat delivered to room vs heat from circuit). |
| `flow_temp_control_type` | `str` | `"Type 2 - Based on outdoor temperature"` | How the **emitter** flow temperature is determined. See control strategies below. |
| `selected_emm_cont_circuit` | `int` | `0` | Index if multiple heating zones/circuits exist (0-based). |
| `mixing_valve` | `bool` | `True` | If a mixing valve is present on emitter circuit (affects achievable flow temp and differential). |
| `mixing_valve_delta` | `float` | `2` | °C delta used when mixing valve is active (typical blending margin). |
| `constant_flow_temp` | `float` (optional) | `42` | Overrides control curve with a constant emitter flow setpoint (°C). *Commented by default*. |

### 2.1 Optional custom emitter tables

You can override internal presets using one or both of the following:

- **`TB14`**: a custom structure/table with manufacturer data (e.g., output vs. ΔT, flow temperature limits). Uncomment and provide your object to replace defaults.
- **`heat_emission_data`**: a compact `pandas.DataFrame` describing key points for the emitter control for a given circuit. Example:

```python
heat_emission_data = pd.DataFrame({
    "θH_em_flw_max_sahz_i": [45],  # Max flow temp (°C) for space-heating zone i
    "ΔθH_em_w_max_sahz_i": [8],    # Max ΔT flow-return (K) for zone i
    "θH_em_ret_req_sahz_i": [20],  # Desired return temp (°C)
    "βH_em_req_sahz_i": [80],      # Desired load factor at ON/OFF (%)
    "θH_em_flw_min_tz_i": [28],    # Minimum flow temp (°C) for zone i
}, index=[
    "Max flow temperature HZ1",
    "Max Δθ flow / return HZ1",
    "Desired return temperature HZ1",
    "Desired load factor with ON-OFF for HZ1",
    "Minimum flow temperature for HZ1"
])
```

> **Tip**: If both `TB14` and `heat_emission_data` are provided, clarify which one your backend prioritizes to avoid ambiguity.

---

## 3) Distribution block (piping network & auxiliaries)

| Field | Type | Example | Meaning |
|---|---|---|---|
| `heat_losses_recovered` | `bool` | `True` | If pipe losses are partly useful to the heated space. |
| `distribution_loss_recovery` | `float` | `90` | % of distribution losses **recovered** inside the conditioned volume. |
| `simplified_approach` | `float` | `80` | % shortcut for simplified loss approach (e.g., rule-of-thumb recovery or reduction). |
| `distribution_aux_recovery` | `float` | `80` | % of auxiliary power (pumps/controls) considered as useful internal gain. |
| `distribution_aux_power` | `float` | `30` | Auxiliary electric power (W) of distribution. |
| `distribution_loss_coeff` | `float` | `48` | Global distribution loss coefficient (W/K) or equivalent scalar used by model. |
| `distribution_operation_time` | `float` | `1` | Fraction of time distribution is active (0..1, per-step multiplier). |

---

## 4) Generator block (plant production side)

| Field | Type | Example | Meaning |
|---|---|---|---|
| `full_load_power` | `float` | `27` | Generator thermal capacity at full load (kW). |
| `max_monthly_load_factor` | `float` | `100` | % cap on monthly load factor (for derating/limitations). |
| `tH_gen_i_ON` | `float` | `1` | Minimum ON time (h) or start-up horizon used for cycling logic. |
| `auxiliary_power_generator` | `float` | `0` | % or W (per model) for generator auxiliary power; used in energy balances. |
| `fraction_of_auxiliary_power_generator` | `float` | `40` | % of generator auxiliaries credited as internal gains. |
| `generator_circuit` | `str` | `"independent"` | Hydraulic layout: `"direct"` or `"independent"` (primary/secondary with HX). |

### 4.1 Generator flow-temperature control

| Field | Type | Example | Meaning |
|---|---|---|---|
| `gen_flow_temp_control_type` | `str` | `"Type A - Based on outdoor temperature"` | Generator flow control strategy (see §5). |
| `gen_outdoor_temp_data` | `pd.DataFrame` | see below | Outdoor reset curve for the generator flow temperature. |
| `speed_control_generator_pump` | `str` | `"variable"` | Pump control mode: `"fixed"` or `"variable"`. |
| `generator_nominal_deltaT` | `float` | `20` | Nominal ΔT (K) across the generator loop. |
| `mixing_valve_delta` | `float` | `2` | If a mixing valve exists on primary, blending margin (°C). |
| `θHW_gen_flw_set` | `float` (opt) | `50` | **Override**: fixed generator flow temperature (°C). |
| `θHW_gen_ret_set` | `float` (opt) | `40` | **Override**: fixed generator return temperature (°C). |

**Example: outdoor reset table**

```python
gen_outdoor_temp_data = pd.DataFrame({
    "θext_min_gen": [-7],   # cold design outdoor temp (°C)
    "θext_max_gen": [15],   # warm boundary (°C)
    "θflw_gen_max": [60],   # flow setpoint at θext_min_gen (°C)
    "θflw_gen_min": [35],   # flow setpoint at θext_max_gen (°C)
}, index=["Generator curve"])
```

The controller interpolates a target flow temperature between `(θext_min_gen, θflw_gen_max)` and `(θext_max_gen, θflw_gen_min)`. Values are clipped outside the range.

---

## 5) Control strategies (cheat sheet)

### 5.1 Emitter `flow_temp_control_type`
Common patterns (implementation-dependent; typical meanings):
- **Type 1 – Constant setpoint**: use `constant_flow_temp` (°C).  
- **Type 2 – Based on outdoor temperature**: emitter flow is computed via an outdoor reset (may reuse the generator curve or a dedicated one).
- **Type 3 – Room feedback**: modulate flow to maintain room operative temperature; requires a PI logic in the backend.
- **Type 4 – Return-limited**: aim for a maximum return temperature (useful in condensing systems).

> **Note**: Your codebase may define the exact meanings of each "Type N". Ensure the UI/CLI lists allowed values.

### 5.2 Generator `gen_flow_temp_control_type`
- **Type A – Based on outdoor temperature**: uses `gen_outdoor_temp_data` (reset curve).  
- **Type B – Constant**: use `θHW_gen_flw_set` and optionally `θHW_gen_ret_set`.  
- **Type C – Demand-following**: track emitter request (requires coupling logic and min/max clamps).

---

## 6) Efficiency model

| Field | Allowed | Notes |
|---|---|---|
| `efficiency_model` | `"simple"`, `"map"`, `"manufacturer"` | `"simple"` applies fixed or curve-based efficiencies. `"map"` uses performance maps. `"manufacturer"` expects detailed tables (COP/η vs. temp/load). |

Backends typically compute **delivered heat**, **electric/primary energy**, and **auxiliary fractions** accordingly.

---

## 7) Calculation options

| Field | Type | Meaning |
|---|---|---|
| `calc_when_QH_positive_only` | `bool` | If `True`, run generator/distribution only when building heating need `Q_H > 0`. |
| `off_compute_mode` | `str` | How to treat the system when off: `"full"` (still compute temps/losses), `"idle"` (minimal), or `"temps"` (only temperatures). |

---

## 8) Units & conventions

- Temperatures in **°C**, ΔT in **K** (numerically the same scale).
- Powers: `kW` for generator/emitter nominal; auxiliaries commonly in **W** (check your backend).
- Efficiencies and fractions input as **percent** (0–100) unless otherwise specified.
- Curves are **per-circuit** unless stated global.
- Time base: typically **hourly** steps.

---

## 9) Validation checklist

- [ ] `nominal_power` ≤ `full_load_power` (kW).  
- [ ] `emission_efficiency` ∈ [0, 100].  
- [ ] `distribution_loss_recovery`, `distribution_aux_recovery` ∈ [0, 100].  
- [ ] `distribution_operation_time` ∈ [0, 1].  
- [ ] Outdoor reset: `θflw_gen_max` ≥ `θflw_gen_min`, `θext_min_gen` < `θext_max_gen`.  
- [ ] If `constant_flow_temp` is set, control type must accept constants.  
- [ ] `generator_circuit` ∈ {`"direct"`, `"independent"`}.  
- [ ] `speed_control_generator_pump` ∈ {`"fixed"`, `"variable"`}.

---

## 10) Minimal working example

```python
INPUT_SYSTEM_HVAC = {
  # Emitter
  "emitter_type": "Floor heating 1",
  "nominal_power": 8,                  # kW
  "emission_efficiency": 90,           # %
  "flow_temp_control_type": "Type 2 - Based on outdoor temperature",
  "selected_emm_cont_circuit": 0,
  "mixing_valve": True,
  "mixing_valve_delta": 2,

  # Distribution
  "heat_losses_recovered": True,
  "distribution_loss_recovery": 90,    # %
  "simplified_approach": 80,           # %
  "distribution_aux_recovery": 80,     # %
  "distribution_aux_power": 30,        # W
  "distribution_loss_coeff": 48,       # W/K (model scalar)
  "distribution_operation_time": 1.0,  # 0..1

  # Generator
  "full_load_power": 27,               # kW
  "max_monthly_load_factor": 100,      # %
  "tH_gen_i_ON": 1,                    # h
  "auxiliary_power_generator": 0,      # (backend-defined units)
  "fraction_of_auxiliary_power_generator": 40,  # %
  "generator_circuit": "independent",

  # Generator control
  "gen_flow_temp_control_type": "Type A - Based on outdoor temperature",
  "gen_outdoor_temp_data": pd.DataFrame({
      "θext_min_gen": [-7],
      "θext_max_gen": [15],
      "θflw_gen_max": [60],
      "θflw_gen_min": [35],
  }, index=["Generator curve"]),

  "speed_control_generator_pump": "variable",
  "generator_nominal_deltaT": 20,      # K
  "mixing_valve_delta": 2,

  # Efficiency
  "efficiency_model": "simple",

  # Options
  "calc_when_QH_positive_only": False,
  "off_compute_mode": "full",
}
```

---

## 11) Advanced customization tips

- **Multiple heating circuits**: use `selected_emm_cont_circuit` to switch presets, or pass a **per-circuit** `heat_emission_data` table.  
- **Manufacturer curves**: provide detailed COP/efficiency maps via `efficiency_model="manufacturer"` and custom data structures.  
- **Hydraulic separation**: with `generator_circuit="independent"`, remember the additional HX ΔT and any mixing valve limits.  
- **Low-temperature systems**: ensure `θflw_gen_min` is compatible with emitter requirements; increase surface area or lower setpoints if needed.

---

<!-- ## 12) Troubleshooting

- **The system never meets setpoint**: check `full_load_power` (kW) and `nominal_power` vs the building peak load. Verify flow-temp curve (too low?).  
- **Return temperature too high**: reduce `ΔθH_em_w_max_sahz_i` or decrease flow temperature; consider increasing emitter area.  
- **Unrealistic distribution losses**: revisit `distribution_loss_coeff` and recovery factors.  
- **Short cycling**: increase `tH_gen_i_ON` and/or use variable-speed pumps.  
- **Fixed temps ignored**: ensure the selected control type actually uses `constant_flow_temp` or explicit `θHW_gen_*` setpoints.

--- -->

## 13) Glossary

- **Emitter**: the device exchanging heat with the room (radiators, floor heating).  
- **Distribution**: pipes, valves, pumps between generator and emitters.  
- **Generator**: heat source (boiler, heat pump, plant loop).  
- **Outdoor reset**: a curve that sets flow temperature based on outdoor air temperature.  
- **ΔT (delta T)**: temperature difference (usually flow minus return).

---

*Prepared for integration with the ISO 15316/52016-based timeseries heating model.*
