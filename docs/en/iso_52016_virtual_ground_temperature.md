# Virtual ground temperature calculation for slab-on-ground floor


```python
def Temp_calculation_of_ground(
    cls,
    building_object,
    lambda_gr=2.0,  # W/(m·K)
    R_si=0.17,      # m²K/W (internal surface resistance)
    R_se=0.04,      # m²K/W (external surface resistance for ground calc.)
    psi_k=0.05,     # W/(m·K) linear transmittance wall/floor junction
    **kwargs        # expects path_weather_file
) -> temp_ground
```

---

### Inputs

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `building_object` | `dict` | — | Building data structure (geometry, envelope, setpoints). See **Required fields** below. |
| `lambda_gr` | `float` | `2.0` | Thermal conductivity of the ground, **W/(m·K)**. |
| `R_si` | `float` | `0.17` | Internal surface resistance, **m²K/W**. |
| `R_se` | `float` | `0.04` | External surface resistance (as used for ground calc.), **m²K/W**. |
| `psi_k` | `float` | `0.05` | Linear thermal transmittance at the wall/floor junction, **W/(m·K)**. |
| `**kwargs['path_weather_file']` | `str | PathLike` | — | Path to EPW used by `Calculation_ISO_52010` to retrieve ambient temperatures. |

#### Required Fields in `building_object`
- `building_parameters.temperature_setpoints.heating_setpoint` (°C)  
- `building_parameters.temperature_setpoints.cooling_setpoint` (°C)  
- `building_surface`: list of surfaces with at least `area`, `sky_view_factor` (used to detect floor-on-ground where `svf == 0`).  
- `building.exposed_perimeter` (m)  
- `building.wall_thickness` (m)  
- *(Optional)* `building.thermal_resistance_floor` (m²K/W). In the current code, `thermal_resistance_floor` is set to **5.3 m²K/W** internally.  
- The function stores `building_parameters.coldest_month` (=1) for later reference.

---

### Purpose
Computes the **virtual ground temperature** and related parameters for **slab-on-ground (SoG)** floors in accordance with **ISO 13370:2017**.  
The routine derives:
- `R_gr_ve`: thermal resistance of the **virtual ground layer** below the floor,
- `Theta_gr_ve`: **monthly virtual ground temperatures** seen by the floor,
- `thermal_bridge_heat`: linear thermal bridge contribution at the **wall–floor junction**.

These quantities are used to model heat exchange with the ground in dynamic/steady-state building energy calculations.


#### How it works

1. **Reference ground resistance**  
   
    \[ R_{gr} = \frac{0.5}{\lambda_{gr}} \quad (\text{m}^2\,K/W) \]

2. **External temperature statistics (monthly)** from `Calculation_ISO_52010` (local time series):  
    - `T2m` → monthly mean / min / max → amplitude of external temperature variations:  
        
        \[ A_e = \frac{\overline{T_{max}} - \overline{T_{min}}}{2} \]  
    
    - Annual external mean: \( \overline{T_e} \).

3. **Internal temperature profile**  
    Using **active heating/cooling setpoints** from the building object:  
    - Annual mean: 
    \( \overline{T_i} = (T_{set,h} + T_{set,c})/2 \)  
    
    - Amplitude: 
    \( A_i = (T_{set,c} - T_{set,h})/2 \)  
    
    - With **coldest month** = 1 (January), monthly internal temperature is:

        \( T_{i,m} = \overline{T_i} - A_i \cos\left(\tfrac{2\pi (m - m_c)}{12}\right) \)

4. **Identify slab-on-ground area (`sog_area`)**  
    The code searches `building_surface` for the element with `sky_view_factor == 0` and uses its `area` as the **contact area with ground**.

5. **Characteristic floor dimension**  
    With **exposed perimeter** `P` and floor area `A`:

    \[ B' = \frac{A}{0.5 P} \]

6. **Equivalent ground thickness**  

    \[ d_t = t_{wall} + \lambda_{gr} (R_{floor} + R_{se}) \]  
    
    where **`R_floor` = 5.3 m²K/W** in this implementation.

7. **Slab-on-ground transmittance** \( U_{sog} \) (ISO 13370 §8):  
    - If \( d_t < B' \) (un/ moderately insulated):
    
        \[ U_{sog} = \frac{2\lambda_{gr}}{\pi B' + d_t} \ln\!\left(\frac{\pi B'}{d_t} + 1\right) \]
    
    - Else (well insulated):  
    
        \[ U_{sog} = \frac{\lambda_{gr}}{0.457 B' + d_t} \]

8. **Virtual layer resistance**  
        
    \[ R_{gr,ve} = \frac{1}{U_{sog}} - R_{si} - R_{floor} - R_{gr} \]

9. **Linear thermal bridges**  
        
    \[ H_{TB} = P \cdot \psi_k \quad (\text{W/K}) \]

10. **Steady-state & periodic ground heat transfer coefficients**  
    - Steady-state: \( H_{ss} = A\,U_{sog} + P\,\psi_k \)  
    
    - Periodic terms (with `periodic_penetration_depth = 3.2 m`):  
      - Internal-side periodic:  

        \[ H_{pi} = A\, \frac{\lambda_{gr}}{d_t} \sqrt{\frac{2}{(1 + \delta)^2 + 1}} \quad \text{with } \delta = \frac{\text{ppd}}{d_t} \]  
      
      - External-side periodic:  

        \[ H_{pe} = 0.37\, P\, \lambda_{gr} \ln\!\left(\frac{\text{ppd}}{d_t} + 1\right) \]

11. **Average heat-flow rate (monthly)**  
    
    \[ \dot{Q}_{avg} = H_{ss}(\overline{T_i} - \overline{T_e}) + Q_{per,i}(m) + Q_{per,e}(m) \] 

    with phase shifts `a_tl = 0` (internal) and `b_tl = 1` (external).

12. **Virtual ground temperature**  
    
    \[ \Theta_{gr,ve}(m) = T_{i,m} - \frac{ \dot{Q}_{avg}(m) - P\,\psi_k (\overline{T_i} - \overline{T_e}) }{A\, U_{sog}} \]

---

### Outputs
The function returns a `temp_ground` wrapper with:

- **`R_gr_ve`** *(float, m²K/W)* – virtual ground-layer thermal resistance below the floor slab.  
- **`Theta_gr_ve`** *(np.ndarray length 12, °C)* – monthly virtual ground temperatures as “seen” by the slab.  
- **`thermal_bridge_heat`** *(float, W/K)* – heat transfer coefficient due to thermal bridges along the exposed perimeter (`exposed_perimeter × psi_k`).

---


### Example 

```python
tg = Temp_calculation_of_ground(
    building_object=bui,
    lambda_gr=2.0,
    R_si=0.17, R_se=0.04,
    psi_k=0.05,
    path_weather_file="../weather/rome.epw",
)
print(tg.R_gr_ve)        # m²K/W
print(tg.Theta_gr_ve)    # array of 12 monthly temperatures (°C)
print(tg.thermal_bridge_heat)  # W/K
```

---

### Notes
- The procedure is explicitly for **slab-on-ground** floors and **conditioned** buildings (not for purely unheated spaces).  
- The floor thermal resistance is **fixed to 5.3 m²K/W** in the code; adjust if your model requires a different construction.  
- Monthly external temperatures are derived from `T2m` in the ISO 52010 weather pipeline; ensure your EPW/PVGIS mapping provides `T2m`.  
- `coldest_month` is set to **January (1)**; adapt for different climates if necessary.  
- The **sog area** is inferred using `sky_view_factor == 0` on a surface; verify this convention matches your data.  

---

### References
- **ISO 13370:2017** — *Thermal performance of buildings — Heat transfer via the ground — Calculation methods*  
- **EN ISO 52010-1:2017** — *External climatic conditions — Solar & meteorological data for energy calculations*

