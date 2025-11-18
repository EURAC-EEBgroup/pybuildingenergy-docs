## <h1 style="color:#df1b12; margin-bottom:0px; font-weight:bold"><strong>Adjacent zone </strong></h1>

The `adj_zone` dictionary provides all necessary geometric and physical properties of an **adjacent unconditioned zone** (e.g., attic, basement, or corridor) required to compute the **transmission heat transfer coefficient** according to **ISO 13789**.


## <h2 style="color:#df1b12; margin-bottom:0px; font-weight:bold"><strong>Adjacent Zone Input (`adj_zone`) </strong></h2>

It is possible to simulate a not conditioned adjacent zone providing the following input: 

**Example Structure:**
```python
{
    "name":"adj_1",
    "orientation_zone": {
        "azimuth": 0,
    },
    "area_facade_elements": np.array([20,60,30,30,50,50], dtype=object),
    "typology_elements": np.array(['OP', 'OP', 'OP', 'OP', 'GR', 'OP'], dtype=object),
    "transmittance_U_elements": np.array([0.82, 0.82, 0.82, 0.82, 0.51, 1.16], dtype=object),
    "orientation_elements": np.array(['NV', 'SV', 'EV', 'WV', 'HOR', 'HOR'], dtype=object),
    'volume': 300, 
    'building_type_class':'Residential_apartment',
    'a_use':50 
}
``` 
---
### Field Descriptions

| Key | Type | Description |
|-----|------|--------------|
| **`name`** | `str` | Identifier of the adjacent zone (e.g., `"adj_1"`). |
| **`orientation_zone.azimuth`** | `float` | The azimuth angle (in degrees) of the unconditioned zone orientation. Used to determine the facing direction (0° = South, 90° = East, 180° = North, 270° = West). |
| **`area_facade_elements`** | `np.array[float]` | Array of surface areas (m²) for each façade element (walls, ground, horizontal slabs, etc.). |
| **`typology_elements`** | `np.array[str]` | Surface type codes following ISO 13789/52016 conventions: <br> - `OP` = *Opaque element (wall)* <br> - `GR` = *Ground-contact surface* <br> - `HOR` = *Horizontal surface (roof/floor)* |
| **`transmittance_U_elements`** | `np.array[float]` | U-values (W/m²·K) corresponding to each façade element, representing their thermal transmittance. |
| **`orientation_elements`** | `np.array[str]` | Orientation of each surface according to ISO 52016 notation: <br> - `NV` = *North Vertical* (north-facing wall) <br> - `SV` = *South Vertical* (south-facing wall) <br> - `EV` = *East Vertical* (east-facing wall) <br> - `WV` = *West Vertical* (west-facing wall) <br> - `HOR` = *Horizontal* (roof or floor) |
| **`volume`** | `float` | Volume (m³) of the adjacent unconditioned zone. Used to estimate ventilation exchange with the external environment. |
| **`building_type_class`** | `str` | Descriptive label for the building type (e.g., `"Residential_apartment"`, `"Office"`, `"Warehouse"`). Used for classification and potential lookup of empirical coefficients. |
| **`a_use`** | `float` | Reference area of the adjacent zone (m²). May be used for normalization or reporting. |

---

### Interpretation of Orientation Codes

| Code | Meaning | Typical Element | Azimuth (°) |
|------|----------|-----------------|--------------|
| **NV** | North Vertical | North-facing opaque wall | 180 |
| **SV** | South Vertical | South-facing opaque wall | 0 |
| **EV** | East Vertical | East-facing opaque wall | 90 |
| **WV** | West Vertical | West-facing opaque wall | 270 |
| **HOR** | Horizontal | Roof or ground-contact surface | — |
| **GR** | Ground | Floor or basement slab | — |

---

### Example Breakdown

For the example above:

| Element | Typology | Orientation | Area (m²) | U-Value (W/m²·K) |
|----------|-----------|--------------|------------|-----------------|
| Wall_1 | OP | NV | 20 | 0.82 |
| Wall_2 | OP | SV | 60 | 0.82 |
| Wall_3 | OP | EV | 30 | 0.82 |
| Wall_4 | OP | WV | 30 | 0.82 |
| Floor | GR | HOR | 50 | 0.51 |
| Roof | OP | HOR | 50 | 1.16 |

---

### Notes
- Arrays in the dictionary (`area_facade_elements`, `U_elements`, `orientation_elements`, etc.) **must have the same length** — one entry per building element.  
- The **azimuth** determines the active orientation for calculations (`NV`, `SV`, `EV`, `WV`, `HOR`).  
- Default ISO convention assumes **0° = South**, rotating clockwise (90° = East, 180° = North, 270° = West).  
- Horizontal (`HOR`) and ground (`GR`) elements contribute to transmission but have no azimuth dependency.

---

### Summary
The `adj_zone` input defines the **geometry and thermal characteristics** of an unconditioned adjacent space.  
It serves as the foundation for ISO 13789 calculations of:
- Transmission losses through opaque and ground-contact elements.
- Ventilation and exchange between conditioned and unconditioned spaces.
- Monthly distribution and adjustment factors for unconditioned zones.


In each not thermal adjacent zone the calcualtion of heat transfer coefficent by transmission is made using the function `transmission_heat_transfer_coefficient_ISO13789`, thta is based to the EN ISO 13789:2017 standard.


---

## <h2 style="color:#df1b12; margin-bottom:0px; font-weight:bold"><strong>Transmission heat transfer coefficients - EN ISO 13789</strong></h2>

---
```python
def transmission_heat_transfer_coefficient_ISO13789(cls, adj_zone, n_ue=0.5, qui=0)
```

### Inputs
| Name | Type | Description |
|------|------|--------------|
| `adj_zone` | `dict` | Dictionary containing the geometric and physical properties of the adjacent (unconditioned) zone. Must include surface orientations, areas, U-values, and volume. |
| `n_ue` | `float`, default `0.5` | Air change rate (h⁻¹) between the unconditioned zone and the external environment. |
| `qui` | `float`, default `0` | Airflow rate (m³/h) between conditioned and unconditioned zones. Typically zero to avoid underestimating transmission. |

---


### Purpose
This function implements the **ISO 13789:2017** method for calculating the **transmission heat transfer coefficient** (`H_tr`) between conditioned, unconditioned, and external zones of a building.  

It provides a quantitative measure of **heat losses through building envelope elements** and **ventilation exchange** with unconditioned spaces and the exterior.


#### How it works

1) **Identify Orientation**

  The function uses the azimuth of the adjacent zone (`adj_zone["orientation_zone"]["azimuth"]`) to map it to an orientation name (`NV`, `SV`, `EV`, `WV`) based on predefined azimuth angles:

  | Orientation | Azimuth (°) |
  |--------------|-------------|
  | NV | 180 |
  | SV | 0 |
  | EV | 90 |
  | WV | 270 |

2) **Extract Arrays**

  From the `adj_zone` dictionary:
  - `areas`: surface areas (m²)  
  - `U_values`: transmittances (W/m²K)  
  - `orientations`: list of orientation strings for each facade element

3) **Boolean Masks**

  Two masks are defined to separate:
  - `mask_selected`: surfaces facing the unconditioned zone  
  - `mask_others`: other external surfaces

4) **Transmission Losses**

  - **Between conditioned and unconditioned zones:**  

\[ H_{d,zt-ztu} = \sum (A_i \cdot U_i) \text{ for selected orientation} \]

  - **From unconditioned zone to exterior:**  

\[ H_{d,ztu-ext} = \sum (A_i \cdot U_i) \text{ for other orientations} \]

5) **Ventilation Losses**

    Ventilation heat transfer coefficients are added according to ISO 13789:

\[ H_{ve,iu} = 0.33 \times q_{iu} \]

\[ H_{ve,ue} = 0.33 \times q_{ue} \]

    Where:
    - `ρ·cp = 0.33 Wh/(m³·K)` for air
    - `q_iu`: airflow between conditioned and unconditioned zones (m³/h)  
    - `q_ue = V_u × n_ue`: airflow between unconditioned zone and exterior

6) **Total Heat Transfer**

\[
H_{ue} = H_{d,ztu-ext} + H_{ve,ue} \\
H_{iu} = H_{d,zt-ztu} + H_{ve,iu}
\]

\[
H_{ztu,tot} = H_{ue} + H_{iu}
\]

7) **Adjustment Factor (b₍ztu₎ₘ)**
    The adjustment factor accounts for the ratio between losses to the exterior and total losses of the unconditioned zone:

\[
b_{ztu,m} = \frac{H_{ue}}{H_{ue} + H_{iu}} = \frac{H_{ue}}{H_{ztu,tot}}
\tag{4.13}
\]

  \(b_{ztu,m}\in[0,1]\) measures how much the unconditioned zone is “anchored” to the **outside** rather than to the **conditioned** neighbor.

8) **Distribution Factor (F₍ztc₎ₘ)**

  If multiple conditioned zones exist, the distribution factor allocates transmission between them:

\[
F_{ztc,ztu,m} = \frac{H_{ztc,i,ztu,m}}{\sum_j H_{ztc,j,ztu,m}}
\]

  Here it is set to `1.0` since only one conditioned zone is assumed.

---


### Physics
The total heat transfer coefficient `H_tr` is computed as:

\[
H_{tr} = H_d + H_g + H_u + H_a
\]

Where:
- **H_d:** Transmission through external envelope (W/K)  
- **H_g:** Transmission through ground (W/K)  
- **H_u:** Transmission through unconditioned zones (W/K)  
- **H_a:** Transmission to adjacent buildings (W/K)  

In this function, we focus on the **unconditioned zone contribution** (`H_u`).

---

### Output

| Variable | Type | Description |
|-----------|------|-------------|
| `H_ztu_tot` | `float` | Total transmission heat transfer coefficient between the conditioned zone and the adjacent unconditioned zone (W/K). |
| `b_ztu_m` | `float` | Monthly adjustment factor for the unconditioned adjacent zone (dimensionless). |
| `F_ztc_ztu_m` | `float` | Distribution factor of the transmission coefficient between conditioned and unconditioned zones (dimensionless). |

---

### Example

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

- `H_ztu_tot` `[W·K⁻¹]` — total coupling of the unconditioned zone.
- `b_ztu_m` `[-]` — monthly factor (in the current code computed once from static inputs).
- `F_ztc_ztu_m` `[-]` — distribution factor (in the current code computed once from static inputs).

Example Output:

```
H_ztu_tot = 78.45  # W/K
b_ztu_m = 0.63
F_ztc_ztu_m = 1.0
```

#### Practical extraction with your `BUI` structure

- For **a given unconditioned zone** `adj_i`:
    - Build sets:
        - \(\mathcal{E}_{zt{\text -}ztu}\): elements in `adj_i` whose `orientation_elements` **match** the interface direction to the conditioned zone (your code uses equality tests by `NV/SV/EV/WV/HOR`).
        - \(\mathcal{E}_{ztu{\text -}ext}\): elements in `adj_i` **not** on the interface.
    - Use `adj_i.volume` → \(V_u\).  
    - Pick `n_ue` from `df_n_ue` by air-tightness class or keep default `0.5 h⁻¹`.


### Edge Cases
- If `A`/`U` vectors contain **dtype=object** (as in your snippet), cast explicitly to `float`.
- If `Hztu_tot = 0` (degenerate geometry), define `b_ztu_m = 1.0` by convention (fully outdoor-anchored).

---

### Notes
- `H_ztu_tot` increases with larger areas, higher U-values, or greater ventilation exchange.  
- Default `n_ue = 0.5` corresponds to “well-sealed joints, no ventilation openings” (ISO 13789 Table 7).  
- The function currently handles **one conditioned zone**; for multiple zones, extend the `F_ztc_ztu_m` calculation.

---

