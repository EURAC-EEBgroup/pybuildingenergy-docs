# CALCULATION PROCEDURE

<div style="background-color: #FA8072; border-left: 4px solid #800000; padding: 10px; margin: 10px 0;">
<strong>Note:</strong> THE ACTUAL CALCULATION OF PRIMARY ENRGY USING THE ISO 15316-1 IS FOR A SINGLE ZONE, IT IS NOT YET IMPLEMENTED THE CALCULATION FOR MULTIPLE ZONES.

</div>

The calculation procedure follows the direction from the energy need to the source (building energy need -> primary energy)




## Description of functions

Herunder explanation of **what the script does** and **comments each function**, with emphasis on:
- assumptions, units of measurement and formulas used;
- structure of input/output data;
- flow of calculation for single step and time series.

> **Standard of reference**: the calculator follows the logic of the **ISO 15316-1** for heating systems and supports 4 types of emission circuits (C.2, C.3, C.4, C.5).
> **Building Energy Need**: The building energy need is calculated using the module ISO 52016. For more information refers to the module ISO 52016.

---

## 1) Overview

- **Main class**: `HeatingSystemCalculator`
- **Input**: a dictionary `input_data` with parameters of **emission**, **distribution** and **generation** (primary).
- **Tabular data**:
  - `TB14` (DF): ISO table with **ΔT nominal** and **exponent n** for the terminal (radiators, panels, etc.).  
    If not provided in `input_data["TB14"]`, uses `TB14_backup` from `global_inputs`.
- **Units** (principali):
  - Energy: **kWh** (exception: `Q_H` can arrive in Wh and is converted)
  - Power: **kW**, Losses/Aux: **kWh**
  - Volumetric flows: **m³/h**
  - Temperature: **°C**
  - **c_w**: specific heat of water in **Wh/(kg·K)** (≈1.16)
- **Output**:
  - for **single step**: dictionary with temperature, flow and energy on emission, distribution and generation;
  - for **time series**: DataFrame hourly/temporal with the same structure.

---

## 2) Class structure

```python
class HeatingSystemCalculator:
    \"\"\"Calcolatore secondo ISO 15316-1 con 4 tipologie C.2–C.5.\"\"\"
```

### `__init__(self, input_data)`
- **What it does**: saves the input, loads **constants** and **parameters** by calling `_load_constants()` and `_load_input_parameters()`.
- **Attention**: `input_data` guides *everything* (control policy, generator efficiency, external curves, etc.).

---

## 3) Loading constants and parameters

### `_load_constants(self)`
- **What it does**: loads **constants** and **parameters** by calling `_load_constants()` and `_load_input_parameters()`. 
- **Details**:
  - If `input_data["TB14"]` is a `pd.DataFrame`, uses it; otherwise uses `TB14_backup`.
  - Set `c_w = 1.16` Wh/(kg·K).
- **Why it is needed**: `TB14` provides nominal ΔT and exponent **n** to calculate the relationship **power ↔ ΔT air-emitter**.

### `_load_input_parameters(self)`
- **What it does**: reads from the input dictionary the parameters of:
  - **Emission (secondary)**: type of emitter, nominal power, efficiency, mixing valve, type of temperature control (demand/external/constant), auxiliary powers, **t** operative, external secondary curve data.
  - **Distribution**: recovery of losses, auxiliary powers, loss coefficient [W/K], service time, etc.
  - **Generation (primary)**: power at full load, maximum load factor, service time, hydraulic scheme (**direct** or **independent**), pump control, nominal ΔT, optional setpoints, generator efficiency model (simple/parametric/manufacturer) and relative curves/parameters, primary circuit temperature control (Type A/B/C) and external primary curve.
- **Important notes**:
  - `selected_emm_cont_circuit` ∈ {0,1,2,3} → C.2/C.3/C.4/C.5.
  - Policy **Q_H ≤ 0**: `calc_when_QH_positive_only` + `off_compute_mode` (`idle`/`temps`/`full`) decide how to handle periods without load.

---

## 4) Default tables and data

### `_default_emission_data(self)`
- **What it provides**: limits/setpoint **secondary** (emission): T supply max, ΔT max, T return desired, load factor with ON/OFF, T min supply.
- **Why it is needed**: it is needed to constrain the calculation of the emitter in function of the demand and the type C.2–C.5.

### `_default_outdoor_data(self)`

- **What it provides**: outdoor **curve (secondary**) defining min/max supply vs. min/max outdoor T..
- **Usage**: used by `calculate_circuit_node_temperature` when the control is "based on outdoor".

---

## 5) Time series data

### `load_csv_data(self, csv_path_or_df)`
- **What it does**: loads time series data from **CSV/DataFrame** with expected columns:
  - `Q_H`, `T_op`, `T_ext` (alias supported).
- **Logic**:
  - If `Q_H` is in **Wh**, creates `Q_H_kWh = Q_H / 1000`.
  - Saves in `self.timeseries_data`.
- **Returns**: loaded DataFrame.

---

## 6) Emission — common parameters

### `calculate_common_emission_parameters(self, heating_needs_kWh, θint)`
- **What it does**: calculates common quantities for C.2–C.5:
  - net demand (after recoverable losses of system),
  - average power emitted `ΦH_em_eff` (kW) on `tH_em_i_ON`,
  - losses/inputs of emission, auxiliary powers,
  - nominal parameters TB14: `ΔθH_em_n`, `ΔθH_em_air`, `nH_em`, nominal flow `V_H_em_nom`.
- **Note**:
  - `V_H_em_nom = ΦH_em_n / (ΔθH_em_n * c_w)`.
  - Calculates **load factor** β and partial ON time for auxiliary powers.

---

## 7) Emission — models C.2/C.3/C.4/C.5

> All use the non-linear relationship **power ↔ ΔT air-emitter** with exponent **n** from TB14.

### `calculate_type_C2(self, common_params, θint)` — **C.2: constant flow, constant water temperature**
- Uses `V_H_em_nom` as **effective flow**.
- Stima `ΔθH_em_air_eff = Δθ_air_nom * (Φ_eff/Φ_nom)^(1/n)`.
- Calculates `θH_em_avg`, then ΔT water `ΔθH_em_w_eff = Φ_eff / (c_w * V)` and from there **supply**/**return** emitter.
- `θH_em_flw_min` include **mixing offset ** se `MIX_EM=True`.

### `calculate_type_C3(self, common_params, θint)` — **C.3: variable flow, constant water temperature (return limited)**
- Fixes `θH_em_ret_set` (≥ `θint`), limits supply (`θH_em_flw_max`, ΔT_w_max).
- Determines `θH_em_flw` and `θH_em_ret` coherent and derives the **flow** from ΔT water.
- `θH_em_flw_min` include mixing offset.

### `calculate_type_C4(self, common_params, θint)` — **C.4: ON–OFF intermittent**
- Uses a **duty cycle** to ensure the energy hourly with power **ON**.
- Determines `θH_em_flw_calc` during ON (from TB14, β required).
- Provides minimum flow for the distribution circuit.

### `calculate_type_C5(self, common_params, θint)` — **C.5: constant flow, variable exchange (bypass)**
- Maintains nominal flow; the **actual flow** is the maximum between the calculation and the minimum set (`θH_em_flw_min_tz_i`).
- The output includes `θH_em_flw_min` (with mixing offset).

---

## 8) Circuit node temperature

### `calculate_circuit_node_temperature(self, θext, emission_results)`
- **What it does**: calculates the **flow at the node** `θH_nod_out` based on the **secondary control type**:
  - **Type 1 – Based on demand**: uses `θH_em_flw_min` of the emission.
  - **Type 2 – Based on outdoor**: uses the **climate curve** secondary.
  - **Type 3 – Constant temperature**: uses `θem_flw_sahz_i` (constant).
- **Output**: `θH_nod_out` (°C).

---

## 9) Operating conditions (secondary)

### `calculate_operating_conditions(self, emission_results, common_params, θint, θH_nod_out)`
- **What it does**: combines the choice C.2/C.3/C.4/C.5 and the node to generate:
  - temperature **circuit**: `θH_cr_flw`, `θH_cr_ret`, flow `V_H_cr`;
  - temperature **distribution** (between collector and emitter): `θH_dis_flw`, `θH_dis_ret`;
  - load factor `βH_em` and minimum flow requested `θH_em_flw_min`;
  - **return emitter** (used downstream).
- **Note**:
  - C.4 introduces ON time and power calculation in ON;
  - C.5 maintains minimum flow and calculates the return from the balance with constant flow.

---

## 10) Distribution

### `calculate_distribution(self, θH_dis_flw, θH_dis_ret, θint, QH_em_i_in)`
- **What it does**: estimates the **distribution losses** and auxiliary powers, the **recoverable** part and the **required** energy input from the distribution.
- **Key formulas**:
  - Losses [kWh] ≈ `((T_media - T_int) * U[W/K] / 1000) * t[h]`
  - Required input: `QH_dis_i_in = QH_dis_i_req + losses - aux - recoveries`
  - Distribution flow: `V_H_dis = QH_dis_i_in / (c_w * ΔT_dis * t)`
- **Output**: dictionary with losses/aux/recoveries and `V_H_dis`.

---

## 11) Generator efficiency (primary)

### `_efficiency_from_model(self, θflw, θret, load_frac=1.0)`
- **What it does**: returns the **efficiency** (%) according to the **selected model**:
  1. **simple**: heuristic in function of `θret` (high condensation at low returns).
  2. **parametric**: piecewise linear model (parameters: `eta_max`, `eta_no_cond`, `T_ret_min`, `T_ret_thr`).
  3. **manufacturer**: curve **1D** (η=f(Tret)) o **2D** (η=f(Tflw,Tret)) con interpolazione bilineare.
- **Note**: clamp a [1, 110] %; fallback a modello semplice se curve non valide.

---

## 12) Primary circuit setpoint

### `_generator_flow_setpoint(self, θext, θH_dis_flw_demand)`
- **What it does**: calculates the **primary circuit setpoint** based on the selected control:
  - **Type A – Outdoor**: uses the **primary curve** (min/max vs T external).
  - **Type B – Demand**: pursues the **secondary demand** (`θH_dis_flw`).
  - **Type C – Constant**: uses `θHW_gen_flw_const`.

---

## 13) Generation (primary)

### `calculate_generation(self, θH_dis_flw, θH_dis_ret, V_H_dis, QH_dis_i_in)`
- **Purpose**:
Calculates the primary circuit thermal output, setpoints, and energy consumption according to the selected control strategy.

- **Control types**:

    -Type A – Outdoor: Uses the primary weather curve (supply temperature as a function of outdoor temperature).
    -Type B – Demand: Follows the secondary circuit demand (θH_dis_flw).
    -Type C – Constant: Uses a fixed setpoint θHW_gen_flw_const.

- **Computation steps**:

    1) **Maximum capacity**:
    max_output_g1 = P_full * LF_max * t
    Defines the maximum hourly energy the generator can deliver.

    2) **Requested output**:
    QH_gen_out = min(QH_dis_i_in, max_output_g1)
    Limits the generator’s output to its capacity.

    3) **Mass and volume flows**:
    ms = ρ * V_dis for the secondary side; primary flow depends on configuration.

    4) **Hydraulic configurations**:

    - **Direct**: primary and secondary circuits are identical.
    - **Independent**: computes ΔT_p, determines the primary supply setpoint (Type A/B/C), applies primary line losses, calculates primary flow mp = Q * 1000 / (c_w * ΔT), and optionally applies anti-dilution logic before finding the return temperature Tp_ret.

    5) **Efficiency**: Re-evaluated using the actual flow/return temperatures via the chosen generator efficiency model.

    6) **Energy balance**:

    - **Input energy**: EHW_gen_in = (QH_gen_out * 100) / η
    - **Auxiliary energy**: EHW_gen_aux = EHW_gen_in * (aux_generator / 100)

    - **Recoverable generator losses**: QW_gen_i_ls_rbl_H
    - **Thermal outputs and split of useful (EH_gen_in) and waste (EWH_gen_in) energy**.

- **Output**: A dictionary containing primary-side temperatures, mass/volume flows, efficiency, and energy consumption for the generator.

---

## 14) Single step execution

### `compute_step(self, q_h_kWh, θint, θext)`
- **Flow**:
  1. Common emission parameters
  2. Emission C.2/C.3/C.4/C.5 (in base a `selected_emm_cont_circuit`)
  3. Calculation **supply node** (secondary)
  4. **Operating conditions** of the circuit
  5. **Distribution**
  6. **Generation** (primary)
  7. Composition of the **output** of the step (dictionary)
- **Returns**: all **temperatures**, **flows** and **energies** of the step.

---

## 15) Time series execution

### `_temps_row_when_off(self, θint, θext)`
- **What it does**: in absence of load (`Q_H ≤ 0`) and with policy `off_compute_mode='temps'`,
  calculates **only the temperatures** significant keeping **powers/flows=0**.

### `run_timeseries(self, df=None)`
- **What it does**: executes the calculation on the entire DataFrame.
- **Alias recognized**:
  - `Q_H_kWh` ↔ `Q_H`, `Q_h`, `Heating_needs`
  - `T_op` ↔ `T_int`, `theta_int`
  - `T_ext` ↔ `theta_ext`
- **Policy when `Q_H ≤ 0`**:
  - `calc_when_QH_positive_only=False`: calculates the **complete flow**.
  - `True` with:
    - `idle`: empty row (NaN/0) — see `_idle_row`.
    - `temps`: row **only temperatures** — see `_temps_row_when_off`.
    - `full`: complete calculation even with null load.
- **Returns**: DataFrame indexed by timestamp with all columns.

---

## 16) Output columns (extracted)

- **Inputs**: `Q_h(kWh)`, `T_op(°C)`, `T_ext(°C)`
- **Emission**: `ΦH_em_eff(kW)`, `θH_em_flow(°C)`, `θH_em_ret(°C)`, `V_H_em_eff(m3/h)`, `θH_em_flw_min_req(°C)`
- **Node/Circuit**: `θH_nod_out(°C)`, `θH_cr_flw(°C)`, `θH_cr_ret(°C)`, `V_H_cr(m3/h)`, `βH_em(-)`
- **Distribution**: `Q_w_dis_i_ls(kWh)`, `Q_w_dis_i_aux(kWh)`, `Q_w_dis_i_ls_rbl_H(kWh)`, `QH_dis_i_in(kWh)`, `V_H_dis(m3/h)`
- **Generation**: `QH_gen_out(kWh)`, `θX_gen_cr_flw(°C)`, `θX_gen_cr_ret(°C)`, `V_H_gen(m3/h)`, `efficiency_gen(%)`, `EHW_gen_in(kWh)`, `EHW_gen_aux(kWh)`


## 17) Best practices and notes

- Verify that `TB14` contains the **rows** for the emitter type (`emitter_type`) and the **columns**:
  - `Emitters_nominal_deltaTeta_Water_C`, `Emitters_nominale_deltaTeta_air_C`, `Emitters_exponent_n`.
- Ensure **Q_H** is provided in **kWh** (or **Wh** with automatic conversion).
- For **independent** circuits, evaluate:
  - `generator_nominal_deltaT`, `gen_flow_temp_control_type`, `θHW_gen_flw_const`,
  - `allow_dilution` and `primary_line_loss` if you want to model the primary hydraulic node with/without dilution.
- The efficiency model can be refined with manufacturer curves (1D/2D) for boilers/heat pumps.

---

## 18) Function → responsibility mapping

| Function | Main responsibility |
|---|---|
| `_load_constants` | Global constants and `TB14` |
| `_load_input_parameters` | Reading all parameters (emission, distribution, generation) |
| `_default_emission_data`, `_default_outdoor_data` | Default for limits/setpoint and secondary circuit curve |
| `load_csv_data` | Loading timeseries and energy normalization |
| `calculate_common_emission_parameters` | Common emission parameters (C.2–C.5) |
| `calculate_type_C2/C3/C4/C5` | Emission models |
| `calculate_circuit_node_temperature` | Compute the secondary node (circuit) supply temperature θH_nod_out according to the selected secondary control policy: based on demand, outdoor, or constant. |
| `calculate_operating_conditions` | Temperature/portate circuito e distribuzione |
| `calculate_distribution` | Losses/auxiliaries/recoveries and distribution flow |
| `_efficiency_from_model` | Generator efficiency according to selected model |
| `_generator_flow_setpoint` | Setpoint mandata primaria (outdoor/demand/costante) |
| `calculate_generation` | Primary circuit balance: useful power, efficiency, consumptions |
| `compute_step` | Pipeline for a single step |
| `_temps_row_when_off` | Row "only temperatures" when Q_H≤0 |
| `run_timeseries` | Execution on the entire time series |

---

## Flowchart (overview)


<pre class="mermaid">
flowchart TD
  A[Start] --> B[__init__]
  B --> C[_load_constants]
  B --> D[_load_input_parameters]
  C --> E{Execution?}
  D --> E

  E -->|single step| F[compute_step]
  E -->|timeseries| TS[run_timeseries]

  subgraph Pipeline["Pipeline compute_step"]
    F --> G[calculate_common_emission_parameters]
    G --> H{Tipo circuito?}
    H -->|C.2| I1[calculate_type_C2]
    H -->|C.3| I2[calculate_type_C3]
    H -->|C.4| I3[calculate_type_C4]
    H -->|C.5| I4[calculate_type_C5]
    I1 --> J[calculate_circuit_node_temperature]
    I2 --> J
    I3 --> J
    I4 --> J
    J --> K[calculate_operating_conditions]
    K --> L[calculate_distribution]
    L --> M[calculate_generation]
    M --> N[Compose outputs dict]
  end

  subgraph Timeseries["Timeseries run_timeseries"]
    TS --> TS0{Row loop}
    TS0 -->|Q_H ≤ 0 AND policy=idle| T0[_idle_row]
    TS0 -->|Q_H ≤ 0 AND policy=temps| T1[_temps_row_when_off]
    TS0 -->|altrimenti| T2[compute_step]
    T0 --> T3[accumula risultati]
    T1 --> T3
    T2 --> T3
  end

  N --> O[Return dict]
  T3 --> P[Return DataFrame]
</pre>


---

## Input/Output tables (main functions)

### 2.1 `__init__(input_data)`
| Field | Type | Description |
|---|---|---|
| `input_data` | dict | Parameters of emission, distribution, generation, policy and tables. |
| **Output** |  | Initializes the instance and calls `_load_constants()` & `_load_input_parameters()`. |

---

### 2.2 `_load_constants()`
| Field | Type | Description |
|---|---|---|
| `input_data["TB14"]` (optional) | `pd.DataFrame` | ISO table with nominal ΔT/esponente; if missing uses `TB14_backup`. |
| **Side-effects** |  | `self.TB14` assigned; `self.c_w = 1.16`. |
| **Output** |  | No explicit return. |

---

### 2.3 `_load_input_parameters()`
| Block | Main keys | Default (example) |
|---|---|---|
| **Emissione** | `emitter_type`, `nominal_power`, `emission_efficiency`, `mixing_valve`, `flow_temp_control_type`, `auxiliars_power`, `emission_operation_time`, `mixing_valve_delta`, `selected_emm_cont_circuit`, `heat_emission_data`, `outdoor_temp_data`, `constant_flow_temp` | `Floor heating`, `8 kW`, `90%`, `True`, `Type 1`, `0 W`, `1 h`, `2 °C`, `0`, `42` |
| **Distribuzione** | `Heat_losses_recovered`, `distribution_loss_recovery`, `simplified_approach`, `distribution_aux_recovery`, `distribution_aux_power`, `distribution_loss_coeff`, `distribution_operation_time`, `recoverable_losses` | `True`, `90%`, `80%`, `80%`, `30 W`, `48 W/K`, `1 h`, `0 kWh` |
| **Generazione** | `full_load_power`, `max_monthly_load_factor`, `tH_gen_i_ON`, `auxiliary_power_generator`, `fraction_of_auxiliary_power_generator`, `generator_circuit`, `speed_control_generator_pump`, `generator_nominal_deltaT`, `θHW_gen_flw_set`, `θHW_gen_ret_set`, `calc_when_QH_positive_only`, `fill_zeros_when_skipped`, `off_compute_mode`, `efficiency_model`, `eta_max`, `eta_no_cond`, `T_ret_min`, `T_ret_thr`, `manuf_curve_1d`, `manuf_curve_2d`, `gen_flow_temp_control_type`, `gen_outdoor_temp_data`, `θHW_gen_flw_const` | `24 kW`, `100%`, `1 h`, `0%`, `40%`, `independent`, `variable`, `20 °C`, `None`, `None`, `True`, `False`, `idle`, `simple`, `110%`, `95%`, `20 °C`, `50 °C`, `None`, `None`, `Type A`, `curve 1D/2D`,`50 °C` |

---

### 2.4 `_default_emission_data()` / `_default_outdoor_data()`
| Function | Output | Note |
|---|---|---|
| `_default_emission_data` | DF con `θH_em_flw_max_sahz_i`, `ΔθH_em_w_max_sahz_i`, `θH_em_ret_req_sahz_i`, `βH_em_req_sahz_i`, `θH_em_flw_min_tz_i` | `Limits/setpoint secondary circuit` |
| `_default_outdoor_data` | DF con `θext_min_sahz_i`, `θext_max_sahz_i`, `θem_flw_max_sahz_i`, `θem_flw_min_sahz_i` | `Secondary circuit limits` |

---

### 2.5 `load_csv_data(csv_path_or_df)`
| Input | Type | Description |
|---|---|---|
| `csv_path_or_df` | str / DataFrame | Timeseries with columns (`Q_H`, `T_op`, `T_ext` or aliases) |
| Output | DataFrame | With optional `Q_H_kWh` added; saved in `self.timeseries_data` |

---

### 2.6 `calculate_common_emission_parameters(heating_needs_kWh, θint)`
| Output (key) | Description |
|---|---|
| `QH_sys_out_hz_i` | Net demand after recoveries |
| `QH_em_i_in` | Energy in at emission |
| `ΦH_em_eff` | Average power on interval (kW) |
| `V_H_em_nom` | Nominal flow (m³/h) |
| `ΔθH_em_n`, `ΔθH_em_air`, `nH_em` | Parameters from TB14 |

---

### 2.7 `calculate_type_C2 / C3 / C4 / C5`
| Function | Principle | Output | Note |
|---|---|---|---|
| `C2` | Constant flow, constant water temperature | `θH_em_flow`, `θH_em_ret`, `V_H_em_eff`, `θH_em_flw_min` | 
| `C3` | Variable flow, constant water temperature (return limited) | `θH_em_flow`, `θH_em_ret`, `V_H_em_eff`, `θH_em_flw_min` | 
| `C4` | **ON–OFF** (duty cycle) | `θH_em_flw_calc`, `θH_em_flw_min`, ecc. | 
| `C5` | Constant flow, variable heat exchange (bypass) | `θH_em_flow=min`, `θH_em_ret≈`, `V_H_em_eff`, `θH_em_flw_min` |

---

### 2.8 `calculate_circuit_node_temperature(θext, emission_results)`
| Control | Logic | Output |
|---|---|---|
| Type 1 | Demand → `θH_em_flw_min` | `θH_nod_out` |
| Type 2 | Secondary circuit limits | `θH_nod_out` |
| Type 3 | Constant (`θem_flw_sahz_i`) | `θH_nod_out` |

---

### 2.9 `calculate_operating_conditions(emission_results, common_params, θint, θH_nod_out)`
| Case | Output | Note |
|---|---|---|
| C.2 / C.3 / C.4 / C.5 | `θH_cr_flw`, `θH_cr_ret`, `V_H_cr`, `θH_dis_flw`, `θH_dis_ret`, `βH_em`, `θH_em_flw_min`, `θH_em_ret_eff` | 

---

### 2.10 `calculate_distribution(θH_dis_flw, θH_dis_ret, θint, QH_em_i_in)`
| Output | Meaning |
|---|---|
| `Q_w_dis_i_ls`, `Q_w_dis_i_aux`, `Q_w_dis_i_ls_rbl_H` | Losses, auxiliaries and recoverable (kWh) |
| `QH_dis_i_req`, `QH_dis_i_in` | Request and effective input to distribution |
| `V_H_dis` | Distribution volumetric flow (m³/h) |

---

### 2.11 `_efficiency_from_model(θflw, θret, load_frac)`
| Model | Description |
|---|---|
| `simple` | Efficiency as function of return temperature (condensation) |
| `parametric` | Piecewise linear with thresholds (`eta_max`, `eta_no_cond`, `T_ret_min`, `T_ret_thr`) |
| `manufacturer` | Manufacturer curves 1D/2D with interpolation |

---

### 2.12 `_generator_flow_setpoint(θext, θH_dis_flw_demand)`
| Type | Logic |
|---|---|
| Type A | Primary curve (outdoor) |
| Type B | Follow secondary demand |
| Type C | Constant |

---

### 2.13 `calculate_generation(θH_dis_flw, θH_dis_ret, V_H_dis, QH_dis_i_in)`
| Output | Meaning |
|---|---|
| `max_output_g1`, `QH_gen_out` | Limit capacity and thermal output (kWh) |
| `θX_gen_cr_flw`, `θX_gen_cr_ret` | Primary circuit effective (°C) |
| `V_H_gen` | Primary circuit volumetric flow (m³/h) |
| `efficiency_gen` | Efficiency (%) |
| `EHW_gen_in`, `EHW_gen_aux` | Energy in ingress and auxiliaries (kWh) |
| `QW_gen_i_ls_rbl_H` | Recoverable losses (kWh) |
| `QW_gen_out`, `QHW_gen_out`, `EH_gen_in`, `EWH_gen_in` | Thermal balances |

---

### 2.14 `compute_step(q_h_kWh, θint, θext)`
| Input | Output |
|---|---|
| `q_h_kWh`, `θint`, `θext` | Dictionary with emission, node/circuit, distribution, generation |

---

### 2.15 `_temps_row_when_off(θint, θext)`
| Purpose | Output |
|---|---|
| Row "only temperature" for `Q_H ≤ 0` | Same keys, with powers/volumes=0 |

---

### 2.16 `run_timeseries(df=None)`
| Input | Output |
|---|---|
| `df` (optional) or `self.timeseries_data` | DataFrame indexed by timestamp with results of each step |

---

## Modelling suggestions

- Verify consistency between **emitter type** and `TB14` rows.  
- For **independent** schemes, curate `generator_nominal_deltaT`, `primary_line_loss` and `allow_dilution`.  
- Use `manufacturer` with realistic manufacturer curves when available.



