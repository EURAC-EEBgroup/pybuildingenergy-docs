## SYSTEM INPUTS

The user must define the following parameters to perform the calculation of primary energy according to EN 15316.1. The python class to which this calculation is requested is the **HeatingSystemCalculator**.

Below is shown an example of a dictionary that must be passed to HeatingSystemCalculator in which the parameters necessary for the calculation are indicated. 
The following parameters are the minimum required, this does not mean that it is possible to modify other parameters based on your own requests.  For example the table TB14 in the hereunder list. 

### EMITTER

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

- **TB14**: it is the table that contains the data of the emitter. If it is not provided the default values are used and the emitter_type is set to the first one in the table.

*Table 3: Emitter data*

| Index | Emitter nominal delta air Temp | Emitter nominal delta water Temp | Emitter exponent | 
|-----------|-------------|------|---------|
| Radiator | 50 | 20 | 1.3 |
| Floor heating | 15 | 5 | 1.1 |
| Fan coil | 25 | 10 | 1.0 |


### GENERATOR


### GENERAL

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

Step by Step Logic 


---
Example of input systems: 
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

    # --- generator ---
    'full_load_power': 27,                  # kW
    'max_monthly_load_factor': 100,         # %
    'tH_gen_i_ON': 1,                       # h
    'auxiliary_power_generator': 0,         # %
    'fraction_of_auxiliary_power_generator': 40,   # %
    'generator_circuit': 'independent',     # 'direct' | 'independent'

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

    # Optional explicit generator setpoints (commented by default)
    # 'θHW_gen_flw_set': 50,
    # 'θHW_gen_ret_set': 40,
}

```

