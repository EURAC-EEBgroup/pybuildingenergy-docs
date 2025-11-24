## <h1 style="color:#df1b12; margin-bottom:0px; font-weight:bold"><strong>HVAC SYSTEM INPUTS</strong></h1>
 

The user must define the following parameters to perform the calculation of primary energy according to EN 15316.1. The python class to which this calculation is requested is the **HeatingSystemCalculator**.

Below is shown an example of a dictionary that must be passed to HeatingSystemCalculator in which the parameters necessary for the calculation are indicated. 
The following parameters are the minimum required, this does not mean that it is possible to modify other parameters based on your own requests.  For example the table TB14 in the hereunder list. 

## <h2 style="color:#df1b12; margin-bottom:0px; font-weight:bold"><strong>EMISSION</strong></h2>


- **Nominal power**: it is the power of the emitter in kW, defined in the product data. 
- **Emission efficiency**: it is the efficiency of the emitter in %.
- **Flow temperature control type**: it is the type of control used to control the flow temperature of the emitter. The possible choice are the ones defined in the "value" column of the following table 


*Table 1: Flow temperature control type*

| Value | Description |
|-----------|-------------|
| Type 1 - Based on demand | The flow temperature is controlled based on the energy demand of the system |
| Type 2 - Based on outdoor temperature | The flow temperature is controlled based on the outdoor temperature |
| Type 3 - Constant temperature | The flow temperature is controlled based on a constant temperature |

- **Emission control circuit**: the value could be from 0 to 3, according to the following table:

*Table 2: Emission control circuit*

| Value | Emission control type | Description |
|-----------|-----------------------|-------------|
| 0 | C2 - Type 1 - Direct Connect | Constant mass flow rate and varying water temperature |
| 1 | C3 - Type 2 - Indipendent flow rate| Varying mass flow (constant temperature) |
| 2 | C4 - Type 3 - Heat exchanger | Intermittent flow rate module, ON-OFF and varying temperature |
| 3 | C5 - Type 4 - Anti-condensate| Constant flow rate and vaiable heat exchange |

- **Mixing valve**: it is a boolean that indicates if a mixing valve is used. It refers to the varaible **MIX_EM**. Possible values: *True* or *False*
- **mixing valve delta**: it is the offset temperature of the mixing valve in °C. It refers to the varaible **mixing_valve_delta**. 

    - The offset refers to the temperature difference between the desired temperature and the actual temperature, which is applied when mixing hot and cold water.

    - In this case, the parameter ΔθH_em_mix_sahz_i represents the temperature offset applied by the mixing valve, with a default value set to 2°C (as defined in the code).

    - This means that when the mixing valve is operating, it will allow a 2°C deviation from the desired temperature to account for system dynamics, such as heat losses, system inertia, or external temperature influences.

- **TB14**: it is the table that contains the data of the emitter. If it is not provided the default values are used and the emitter_type is set to the first one in the table.

*Table 3: Emitter data*

| Index | Emitter nominal delta air Temp | Emitter nominal delta water Temp | Emitter exponent | 
|-----------|-------------|------|---------|
| Radiator | 50 | 20 | 1.3 |
| Floor heating | 15 | 5 | 1.1 |
| Fan coil | 25 | 10 | 1.0 |


**heat_emission_data**: it is the table that contains the data of the emission circuit. If it is not provided the default values are used and the emitter_type is set to the first one in the table. In the code we have the function `_default_emission_data()` that returns the default values.
These values are default emission circuit parameters for the heating system’s **secondary side** (the side connected to heating emitters, such as radiators or underfloor heating).  
 They represent **nominal** and **operational setpoints** for a single heating zone (HZ1), including flow/return temperatures and load control factors.

*Table 4: Emission circuit data*

| **Parameter (column name)**      | **Description**                                                     | **Default Value** | **Unit** |
|----------------------------------|---------------------------------------------------------------------|------------------:|:---------:|
| `θH_em_flw_max_sahz_i`           | Maximum flow temperature for the heating emission circuit           | 45               | °C        |
| `ΔθH_em_w_max_sahz_i`            | Maximum water flow/return temperature difference                    | 8                | °C        |
| `θH_em_ret_req_sahz_i`           | Desired return temperature of the emission circuit                  | 20               | °C        |
| `βH_em_req_sahz_i`               | Desired load factor with ON/OFF control                             | 80               | %         |
| `θH_em_flw_min_tz_i`             | Minimum required flow temperature for the thermal zone              | 28               | °C        |

---

## <h2 style="color:#df1b12; margin-bottom:0px; font-weight:bold"><strong>DISTRIBUTION</strong></h2> 

```python 
# --- distribution ---
'heat_losses_recovered': True,
'distribution_loss_recovery': 90,
'simplified_approach': 80,
'distribution_aux_recovery': 80,
'distribution_aux_power': 30,
'distribution_loss_coeff': 48,
'distribution_operation_time': 1,
```
The parameters are used inside the class **HeatingSystemCalculator** as:

```python
self.Heat_losses_recovered = inp.get('heat_losses_recovered', True)
self.f_h_dist_i_ls = inp.get('distribution_loss_recovery', 90)  # %
self.simplified_or_holistic_approach = inp.get('simplified_approach', 80)  # %
self.f_h_dist_i_aux = inp.get('distribution_aux_recovery', 80)  # %
self.W_H_dist_i_aux = inp.get('distribution_aux_power', 30)  # W
self.Heat_loss_coefficent_dist = inp.get('distribution_loss_coeff', 48)  # W/K
self.tH_dis_i_ON = inp.get('distribution_operation_time', 1)  # h
```

if data is not provided by the user, the default values are used.

These parameters describe the **thermal and electrical behavior** of the **heat distribution subsystem**, which connects the generator to the emitters (secondary circuits).  
They define how heat losses, auxiliary energy use, and simplifications in the calculation are handled within the EN 15316-1 framework.

| **Variable** | **Description** | **Default** | **Unit** |
|---------------|-----------------|-------------|----------|
| `heat_losses_recovered` | Boolean flag that defines whether **distribution heat losses** are considered **recoverable** in the building (e.g., heat lost in indoor piping contributes to heating). | `True` | – |
| `distribution_loss_recovery` (`f_h_dist_i_ls`) | Fraction of distribution losses that are **recoverable** (typically within the heated zone). | `90` | % |
| `simplified_approach` (`simplified_or_holistic_approach`) | Defines the calculation approach for recovered losses: a **simplified method** (`> 0`) or a **holistic method** (`0` for detailed ISO modeling). | `80` | % |
| `distribution_aux_recovery` (`f_h_dist_i_aux`) | Fraction of **auxiliary electrical power** (e.g., pumps, valves) that is **converted into useful heat** and recovered within the heated space. | `80` | % |
| `distribution_aux_power` (`W_H_dist_i_aux`) | Rated **auxiliary electrical power** of the distribution system (e.g., circulation pumps). | `30` | W |
| `distribution_loss_coeff` (`Heat_loss_coefficent_dist`) | Overall **heat loss coefficient** of the distribution system, representing thermal losses per degree of temperature difference between the fluid and ambient air. | `48` | W/K |
| `distribution_operation_time` (`tH_dis_i_ON`) | Average **operation time** of the distribution system per time step (typically the same as the emission system). | `1` | h |

---


## <h2 style="color:#df1b12; margin-bottom:0px; font-weight:bold"><strong>GENERATION</strong></h2>

The generator is modelled using the following parameters:

```python
    # --- generator ---
    'full_load_power': 27,                  # kW
    'max_monthly_load_factor': 100,         # %
    'tH_gen_i_ON': 1,                       # h
    'auxiliary_power_generator': 0,         # %
    'fraction_of_auxiliary_power_generator': 40,   # %
    'generator_circuit': 'independent',     # 'direct' | 'independent'
    'gen_flow_temp_control_type': 'Type A - Based on outdoor temperature',
    'gen_outdoor_temp_data': pd.DataFrame({
        "θext_min_gen": [-7],
        "θext_max_gen": [15],
        "θflw_gen_max": [60],
        "θflw_gen_min": [35],
    }, index=["Generator curve"])
    'θHW_gen_flw_const': 50.0
    # Optional explicit generator setpoints (commented by default)
    # 'θHW_gen_flw_set': 50,
    # 'θHW_gen_ret_set': 40,
    'speed_control_generator_pump': 'variable',
    'generator_nominal_deltaT': 20
```

That are:
<br>

- **load power**: it is the power of the generator in kW, defined in the product data. variable name: 'full_load_power'
- **max monthly load factor**: it is the maximum load factor of the generator in %.  variable_name: 'max_monthly_load_factor'
- **tH_gen_i_ON**: it is the time of the generator in ON state in hours. variable_name: 'tH_gen_i_ON'
---
- **auxiliary power generator**: Percentage of generator input energy used by auxiliary systems (generally 0-5 %).Increases total system energy input. variable_name: 'auxiliary_power_generator'
- **fraction of auxiliary power generator**: it is the portion of auxiliary energy recovered as heat (generally 20–60%). Reduces auxiliary losses.variable_name: 'fraction_of_auxiliary_power_generator'.

    <br>
    <u>**1. `auxiliary_power_generator`**</u>
    This parameter defines **how much additional electrical power** (in %) is consumed by the generator’s own auxiliary components, such as:

    - Circulation pumps  
    - Combustion or ventilation fans  
    - Electronic controls and sensors  
    - Ignition systems  
    - Internal electronics (standby mode)

    **Formula**:

    \[
    E_{HW,gen,aux} = E_{HW,gen,in} \times \frac{\text{auxiliary\_power\_generator}}{100}
    \]

    Where:

    - \( E_{HW,gen,in} \): Generator input energy (kWh)  
    - \( E_{HW,gen,aux} \): Auxiliary energy consumed (kWh)
    
    <br>
    <u>**2. `fraction_of_auxiliary_power_generator`**</u>

    This parameter represents **the fraction of auxiliary power that is recoverable as useful heat**.  
    Some auxiliary systems release heat that can be recovered by the generator’s thermal circuit.

    For example:
    - Pump motors or internal electronics may release part of their heat to the water loop.  
    - Fans or controllers might dissipate energy inside the generator casing.

    **Formula**:

    \[
    Q_{W,gen,i,ls,rbl,H} = E_{HW,gen,aux} \times \frac{\text{fraction_of_auxiliary_power_generator}}{100}
    \]

    Where:

    - \( Q_{W,gen,i,ls,rbl,H} \): Recovered auxiliary heat (kWh)

---
- **generator circuit**: it is the circuit of the generator. It can be 'direct' or 'independent'. variable_name: 'generator_circuit'
    - **Direct**: the generator is connected to the primary circuit, no hydraulic separation primary = secondary
    - **Independent**: the generator is connected to the secondary circuit, with hydraulic separator primary != secondary

The primary circuit supply temperature setpoint (Tp_sup_set), i.e., the flow temperature on the generator side (boiler, heat pump, etc.) is calculated using the function **_generator_flow_setpoint(θext, θH_dis_flw_demand)**, according to the selected control strategy of the generation system

It determines how hot the generator should make the supply water based on:
- the outdoor temperature **(θext)**, and/or
- the heating demand from the distribution/emission side **(θH_dis_flw_demand)**, and/or
- a fixed setpoint defined by the user.

The input parameters of the function are:

- **θext**: outdoor air temperature
- **θH_dis_flw_demand**: Flow temperature requested by the secondary circuit (distribution/emission side)

with global inputs that are:

- **df_gen_out_temp**: Table defining the primary (generator) heating curve
- **gen_flow_temp_control_type**: Type of control used to control the flow temperature of the generator.Defines which control strategy is used (“Type A”, “Type B”, “Type C”):

    - 'Type A - Based on outdoor temperature': uses primary's own weather curve
    - 'Type B - Based on demand'            : follows the secondary demand (θH_dis_flw)
    - 'Type C - Constant temperature'       : uses θHW_gen_flw_const

- **θHW_gen_flw_const**: Constant flow temperature of the generator

The user should provide the information directly in the dictionary:

```python 
'gen_flow_temp_control_type': 'Type A - Based on outdoor temperature',
'gen_outdoor_temp_data': pd.DataFrame({
    "θext_min_gen": [-7],
    "θext_max_gen": [15],
    "θflw_gen_max": [60],
    "θflw_gen_min": [35],
}, index=["Generator curve"])
'θHW_gen_flw_const': 50.0
```

where, in the code are defined as: 

```python 
self.df_gen_out_temp = inp.get('gen_outdoor_temp_data', pd.DataFrame({
    "θext_min_gen": [-7],
    "θext_max_gen": [15],
    "θflw_gen_max": [60],   # °C, max primary supply
    "θflw_gen_min": [35],   # °C, min primary supply
}, index=["Generator curve"]))

self.gen_flow_temp_control_type = inp.get(
    'gen_flow_temp_control_type',
    'Type A - Based on outdoor temperature'   # 'Type A' | 'Type B' | 'Type C'
)

self.θHW_gen_flw_const = float(inp.get('θHW_gen_flw_const', 50.0))
```
Explanation of the different type of control:

- <u> Type A - Based on outdoor temperature. Climatic curve (outdoor compensation)</u>
```python 
if ctrl.startswith('Type A'):
    if θext_max != θext_min:
        Tp = θflw_min + (θflw_max - θflw_min) * (θext_max - θext) / (θext_max - θext_min)
        return max(min(Tp, θflw_max), θflw_min)
    return θflw_min
```
Calculates the generator flow temperature linearly based on outdoor temperature.
**Equation**:
The generator flow temperature \( T_{p, \text{set}} \) is calculated linearly based on the outdoor temperature \( \theta_{\text{ext}} \), following the formula:

\[
T_{p, \text{set}} = T_{\text{flw}, \text{min}} + \left( T_{\text{flw}, \text{max}} - T_{\text{flw}, \text{min}} \right) \cdot \frac{\left( \theta_{\text{ext}, \text{max}} - \theta_{\text{ext}} \right)}{\left( \theta_{\text{ext}, \text{max}} - \theta_{\text{ext}, \text{min}} \right)}
\]

Where:

- \( T_{\text{flw}, \text{min}} \) = minimum flow temperature (e.g., 35°C)
- \( T_{\text{flw}, \text{max}} \) = maximum flow temperature (e.g., 60°C)
- \( \theta_{\text{ext}} \) = outdoor air temperature
- \( \theta_{\text{ext}, \text{min}} \) = minimum outdoor temperature (e.g., -7°C)
- \( \theta_{\text{ext}, \text{max}} \) = maximum outdoor temperature (e.g., 15°C)
The calculated \( T_{p, \text{set}} \) is then clamped between the minimum and maximum values:

\[
T_{p, \text{set}} = \max\left( \min\left( T_{p, \text{set}}, T_{\text{flw}, \text{max}} \right), T_{\text{flw}, \text{min}} \right)
\]

👉🏻 **Meaning**: This is the typical weather-compensated control used (for example) in boilers and heat pumps.
It automatically adjusts water temperature to the outdoor conditions for better efficiency and comfort.
**Example visualization of type A:**
```python
Generator flow temperature (°C)
│
│    60°C ────┐
│              \
│               \
│                \
│                 \
│    35°C ────────────────┘──────────────► Outdoor temperature (°C)
          -7          0           +15
```

- <u> Type B - Based on demand. Follow secondary demand</u>
```python 
if ctrl.startswith('Type B'):
    return float(θH_dis_flw_demand)
```
Sets the generator supply temperature equal to the **demand from the secondary (distribution/emission) side.**
👉🏻 **Meaning**: This is used in systems with hydraulic separation (e.g., with a buffer tank or heat exchanger) where the generator must match the needs of the secondary circuit dynamically.
**Example**:
If the radiator loop requests 45 °C → the generator must deliver exactly 45 °C to maintain balance.

- <u> Type C - Constant temperature</u>
```python 
return float(self.θHW_gen_flw_const)
```
Ignores weather and demand — the generator runs at a fixed supply temperature (e.g., 50 °C).
👉🏻 **Meaning**: Simplest and oldest control type, often found in small or legacy heating systems.
It offers no adaptation to weather or load, typically less efficient.
**Example**:
If the user defines a constant supply temperature of 50 °C → the generator will always deliver 50 °C, regardless of the demand from the secondary circuit.
---

- **speed control of generator pump**: icontrols **how ΔT varies with system load** (constant vs variable). It can be in the code 'variable' or 'deltaT_constant'. variable_name: 'speed_control_generator_pump'
- **Nominal water deltaT of generator**: defines **the nominal ΔT at design (full load)** — the reference used in thermal balance equations in °C. variable_name: 'generator_nominal_deltaT'. It is used if speed_control_of_generator_pump is 'deltaT_constant'.

    **More info**:

    - **`"deltaT_constant"`** → The pump maintains a **fixed temperature difference (ΔT)** between flow and return.
    - Example: The pump adjusts its speed so that ΔT = 20 °C remains constant.
    - **`"variable"`** → The pump **varies its speed dynamically** according to the system load.
    - When heating demand decreases, the water flow rate decreases.
    - This leads to a smaller ΔT at partial loads, improving efficiency.

    When `variable`, the temperature difference (ΔT) **decreases proportionally with the thermal load**, which represents **real modulating behavior** of pumps and heat generators.

    ---

    <u>**`generator_nominal_deltaT`**</u>

    Defines the **nominal temperature difference (ΔT)** between the **generator flow** and **return** at **full-load conditions**.

    \[
    \Delta T_{nom} = T_{flow,nominal} - T_{return,nominal}
    \]

    This is the **design operating condition** for the generator, used as a reference in calculations.

    <u>Example:</u>

    If `generator_nominal_deltaT = 20`, then at full load:

    - Supply temperature = 60 °C  
    - Return temperature = 40 °C  
    → ΔT = 20 °C  

    At partial load:

    - If `speed_control_generator_pump = "deltaT_constant"` → ΔT remains **20 °C**.  
    - If `speed_control_generator_pump = "variable"` → ΔT may drop to **10–15 °C**, depending on demand.

--- 

It is possible to define the optional primary setpoints (used if circuit is independent).

- **θHW_gen_flw_set**: flow temperature setpoint
- **θHW_gen_ret_set**: return temperature setpoint

---

## <h2 style="color:#df1b12; margin-bottom:0px; font-weight:bold"><strong>GENERAL</strong></h2>

---
**Efficiency model**

The calculation of efficiency can be done using three type of choices: 

    1) 'simple'       : linear heuristic vs. return temperature
    2) 'parametric'   : piecewise/threshold model
    3) 'manufacturer' : 1D (return) or 2D (flow/return) map

the calculation is made using the function **_efficiency_from_model()** that requires one of the above options: simple, parameteric, manufacturer.
It calculates how efficiently the generator converts input energy (like gas, electricity, or fuel) into useful heat, depending on the flow (θflw) and return (θret) water temperatures on the primary circuit side.
Explanation of each option:

1) **'simple'**: it is a linear heuristic based on the return temperature. 
```python
if model == 'simple':
    if θret < 50.0:
        eff = 110.0 - 0.5 * (θret - 20.0)
    else:
        eff = 95.0
    return max(min(eff, 110.0), 1.0)

```
This is a simplified heuristic formula typically used for condensing boilers:

- When the **return temperature (θret)** is **below 50°C**, condensation occurs in the flue gases, recovering latent heat. 
    → The efficiency increases up to ~110% (based on lower heating value, PCI).
- When **θret ≥ 50°C**, condensation stops, and the efficiency drops to around 95%.

**Meaning:**
| Condition | Return Temp | Typical Generator Behavior | Efficiency |
Condesning mode | < 50°C | Flue gas condensation → higher recovery | 95-110% |
Ono-condensing |  ≥ 50°C | No condensation | ~95% |

2) **'parametric'**: it is a piecewise/threshold model based on the linear interpolation of return temperature. 
```python
if model == 'parametric':
    eta_max = self.eta_max
    eta_nc  = self.eta_no_cond
    T_min   = self.T_ret_min
    T_thr   = self.T_ret_thr

    Tret_clip = max(min(θret, T_thr), T_min)
    slope = (eta_max - eta_nc) / (T_min - T_thr)
    if θret <= T_thr:
        eff = eta_max + slope * (Tret_clip - T_min)
    else:
        eff = eta_nc

```
This is a **parameterized linear model** that allows flexible configuration without a full manufacturer curve:

- **eta_max**: maximum efficiency (e.g., 110%) when return temperature is low (T_min)
- **eta_nc**: non-condensing efficiency (e.g., 95%) when return temperature is high (T_thr)
- **T_min**: minimum return temperature (lower bound of condensing operation)
- **T_thr**: threshold temperature where condensation ceases

The function linearly interpolates between these two operating points.

**Meaning:**

| Region |  Return Temp | Efficiency trend | 
|--------|--------------|------------------|
| Region 1 | θret <= T_thr | Linear decrease from η_max (at T_min) to η_nc (at T_thr) |
| Region 2 | θret > T_thr | Constant η_nc (no more condensation)|

This model offers a tunable middle ground between the simple heuristic and a full manufacturer curve — it’s ideal for parametric studies or sensitivity analyses.

3) **'manufacturer'**: it is a 1D (return) or 2D (flow/return) map based on the manufacturer curve. 
```python
if model == 'manufacturer':
    # (a) 1D curve eff = f(Tret)
    # (b) 2D surface eff = f(Tflw, Tret)
```

This model uses **real efficiency maps** provided by the equipment manufacturer.

**(a) 1D curve**

- The efficiency is interpolated from a list of measured points: Tret = [20, 30, 40, 50, 60], eta = [109, 106, 101, 95, 93].
- Uses linear interpolation to find the efficiency for the given θret.

**(b) 2D surface**

- For more detailed manufacturer data, efficiency is given as a grid (matrix) depending on both flow and return temperatures.
- Bilinear interpolation is used between the four nearest points (Q11, Q12, Q21, Q22) to compute an accurate efficiency value.

**Meaning:**

| Type | Inputs | Accuracy | Typical Use |
|------|--------|----------|-------------|
| 1D | Return temperature only | Moderate | Simplified manufacturer data |
| 2D | Flow + return temperatures | High | Detailed boiler performance maps |

If the manufacturer data is missing or invalid, the function falls back to the simple heuristic.

---

**Calculation Model:**

```python
    'calc_when_QH_positive_only': False,
    'off_compute_mode': 'full'
```

It controls **what the program does when the heating demand (Q_H) is zero or negative** — i.e., when there is **no heating load** required in that timestep.

Every timestep in the timeseries (typically 1 hour) has:

- **qh** → heating demand in kWh
- **θint** → indoor air temperature
- **θext** → outdoor temperature

The model decides how to behave based on the value of qh and the user-defined policy flags:

- **calc_when_QH_positive_only**
- **off_compute_mode**

These two flags **control what happens when the heating load = 0.**

**Step by Step Logic**

**1) Detect zero or negative heating demand**

```python
if float(qh) <= 0:
```
This means there is no heating required (or possibly cooling).
Now the function checks which policy is set for such cases.

**2) Case 1 — Full simulation even when Q_H = 0**
```python 
if not self.calc_when_QH_positive_only:
    # Full calculation even with zero load
    res = self.compute_step(0.0, float(θint), float(θext))
    ...
```

- Here, the flag *calc_when_QH_positive_only* is False, so the user wants to compute everything even when there’s no load.
- It runs the complete thermal balance by calling:
```python  
res = self.compute_step(0.0, float(θint), float(θext))
```
This means: compute system temperatures, efficiencies, flow rates, etc., as if the system were still active but with zero heating power.

- The results are appended to the output DataFrame as usual.

**Use case:** See how the system behaves under “no load” conditions (e.g., during shoulder months) — including standby losses or auxiliary power.

**3) Case 2 — Skip detailed calculation (calc_when_QH_positive_only = True)**

If this flag is True, the system should behave differently depending on how “off periods” are treated.

There are three “off modes” controlled by *self.off_compute_mode.*
 
- <u> a) Mode: **'idle'** → Minimal record </u>
```python
if self.off_compute_mode == 'idle':
    res_row = {'timestamp': idx}
    res_row.update(self._idle_row(0.0, float(θint), float(θext)))
```
    - Produces a minimal output line using _idle_row().
    - This function fills the row mostly with zeros or NaN values — representing that nothing is being calculated because the system is idle.
    - Only basic fields like timestamp, indoor temperature, and outdoor temperature are kept.

    👉🏻 **Use case**: For speed optimization when simulating a full year — avoids doing unnecessary physics calculations.

- <u> b) Mode: **'temps'** → Record only temperatures </u>
```python
elif self.off_compute_mode == 'temps':
    res = self._temps_row_when_off(float(θint), float(θext))
```
    - This still computes temperatures (like circuit or node flow/return) using _temps_row_when_off(),
    - but all energetic terms (flows, powers, losses) are set to zero.
    - This way, you can visualize how the temperature control or mixing valves behave even with zero heating demand.

    👉🏻 **Use case**: For continuous temperature mapping, useful when validating system controls or comfort conditions.

- <u> c) Mode: **'full'** → Full calculation despite Q_H = 0 </u>
```python
elif self.off_compute_mode == 'full':
    res = self.compute_step(0.0, float(θint), float(θext))
```
    - Similar to Case 1 but triggered explicitly by mode 'full' — performs a complete computation of all variables even if load = 0.
    - This is a “force full calc” inside the zero-demand policy.

    👉🏻 **Use case**: When testing or debugging; ensures identical data structure across all timesteps.

**4) continue statements**

Each branch ends with *continue* —
→ meaning the loop moves to the next timestep immediately after handling this case.
No further code in the timestep is executed once the “zero-load” policy has been applied.

**General-physical interpretation** 

This logic helps balance accuracy vs performance:

In annual simulations (8760 hours), 70–90% of the time may have zero heating demand (e.g., in summer).
Recomputing all hydraulic and thermal equations each hour would waste time.

Therefore, this control allows skipping unnecessary computations or simplifying the result depending on your simulation purpose:

- **"idle"** → fastest
- **"temps"** → medium (keep comfort analysis)
- **"full"** → slowest but most complete

---
**Example of inputs system:** 
```python
INPUT_SYSTEM_HVAC  = {
    
    # ---- emitter ----
    'emitter_type': 'Floor heating',
    'nominal_power': 8,
    'emission_efficiency': 90,
    'flow_temp_control_type': 'Type 2 - Based on outdoor temperature',
    'selected_emm_cont_circuit': 0,
    'mixing_valve': True,
    # 'TB14': custom_TB14, #  <- Uncomment and upload your emittere table, oterwhise the default stored in gloabl_inputs.py is used
    'heat_emission_data' : pd.DataFrame({
            "θH_em_flw_max_sahz_i": [45],
            "ΔθH_em_w_max_sahz_i": [8],
            "θH_em_ret_req_sahz_i": [20],
            "βH_em_req_sahz_i": [80],
            "θH_em_flw_min_tz_i": [28],
        }, index=[
            "Max flow temperature HZ1",
            "Max Δθ flow / return HZ1",
            "Desired return temperature HZ1",
            "Desired load factor with ON-OFF for HZ1",
            "Minimum flow temperature for HZ1"
        ])

    # --- distribution ---
    'heat_losses_recovered': True,
    'distribution_loss_recovery': 90,
    'simplified_approach': 80,
    'distribution_aux_recovery': 80,
    'distribution_aux_power': 30,
    'distribution_loss_coeff': 48,
    'distribution_operation_time': 1,

    # --- generator ---
    'full_load_power': 27,                  # kW
    'max_monthly_load_factor': 100,         # %
    'tH_gen_i_ON': 1,                       # h
    'auxiliary_power_generator': 0,         # %
    'fraction_of_auxiliary_power_generator': 40,   # %
    'generator_circuit': 'independent',     # 'direct' | 'independent'
    # Optional explicit generator setpoints (commented by default)
    # 'θHW_gen_flw_set': 50,
    # 'θHW_gen_ret_set': 40,
    # Primary: independent climatic curve
    'gen_flow_temp_control_type': 'Type A - Based on outdoor temperature',
    'gen_outdoor_temp_data': pd.DataFrame({
        "θext_min_gen": [-7],
        "θext_max_gen": [15],
        "θflw_gen_max": [60],
        "θflw_gen_min": [35],
    }, index=["Generator curve"]),

    'speed_control_generator_pump': 'variable',
    'generator_nominal_deltaT': 20,         # °C

    # Efficiency model
    'efficiency_model': 'simple',

    # Calculation options
    'calc_when_QH_positive_only': False,
    'off_compute_mode': 'full',
}

```

