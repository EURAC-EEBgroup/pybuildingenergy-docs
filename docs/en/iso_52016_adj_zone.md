# Adjacent zone

The `adj_zone` dictionary provides all necessary geometric and physical properties of an **adjacent unconditioned zone** (e.g., attic, basement, or corridor) required to compute the **transmission heat transfer coefficient** according to **ISO 13789**.


## Adjacent Zone Input (`adj_zone`)
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



Function: `transmission_heat_transfer_coefficient_ISO13789(adj_zone, n_ue=0.5, qui=0)`
---

### Purpose
This function implements the **ISO 13789:2017** method for calculating the **transmission heat transfer coefficient** (`H_tr`) between conditioned, unconditioned, and external zones of a building.  

It provides a quantitative measure of **heat losses through building envelope elements** and **ventilation exchange** with unconditioned spaces and the exterior.

---

### Function Signature
```python
def transmission_heat_transfer_coefficient_ISO13789(cls, adj_zone, n_ue=0.5, qui=0)
```

### Parameters
| Name | Type | Description |
|------|------|--------------|
| `adj_zone` | `dict` | Dictionary containing the geometric and physical properties of the adjacent (unconditioned) zone. Must include surface orientations, areas, U-values, and volume. |
| `n_ue` | `float`, default `0.5` | Air change rate (h⁻¹) between the unconditioned zone and the external environment. |
| `qui` | `float`, default `0` | Airflow rate (m³/h) between conditioned and unconditioned zones. Typically zero to avoid underestimating transmission. |

---

### Returns
| Variable | Type | Description |
|-----------|------|-------------|
| `H_ztu_tot` | `float` | Total transmission heat transfer coefficient between the conditioned zone and the adjacent unconditioned zone (W/K). |
| `b_ztu_m` | `float` | Monthly adjustment factor for the unconditioned adjacent zone (dimensionless). |
| `F_ztc_ztu_m` | `float` | Distribution factor of the transmission coefficient between conditioned and unconditioned zones (dimensionless). |

---

### Physical Background
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

### Step-by-Step Algorithm

#### 1 Identify Orientation
The function uses the azimuth of the adjacent zone (`adj_zone["orientation_zone"]["azimuth"]`) to map it to an orientation name (`NV`, `SV`, `EV`, `WV`) based on predefined azimuth angles:

| Orientation | Azimuth (°) |
|--------------|-------------|
| NV | 180 |
| SV | 0 |
| EV | 90 |
| WV | 270 |

#### 2 Extract Arrays
From the `adj_zone` dictionary:
- `areas`: surface areas (m²)  
- `U_values`: transmittances (W/m²K)  
- `orientations`: list of orientation strings for each facade element

#### 3 Boolean Masks
Two masks are defined to separate:
- `mask_selected`: surfaces facing the unconditioned zone  
- `mask_others`: other external surfaces

#### 4 Transmission Losses
- **Between conditioned and unconditioned zones:**  

  \[ H_{d,zt-ztu} = \sum (A_i \cdot U_i) \text{ for selected orientation} \]
- **From unconditioned zone to exterior:**  

  \[ H_{d,ztu-ext} = \sum (A_i \cdot U_i) \text{ for other orientations} \]

#### 5 Ventilation Losses
Ventilation heat transfer coefficients are added according to ISO 13789:

\[ H_{ve,iu} = 0.33 \times q_{iu} \]

\[ H_{ve,ue} = 0.33 \times q_{ue} \]

Where:
- `ρ·cp = 0.33 Wh/(m³·K)` for air
- `q_iu`: airflow between conditioned and unconditioned zones (m³/h)  
- `q_ue = V_u × n_ue`: airflow between unconditioned zone and exterior

#### 6 Total Heat Transfer
\[
H_{ue} = H_{d,ztu-ext} + H_{ve,ue} \\
H_{iu} = H_{d,zt-ztu} + H_{ve,iu}
\]

\[
H_{ztu,tot} = H_{ue} + H_{iu}
\]

#### 7 Adjustment Factor (b₍ztu₎ₘ)
The adjustment factor accounts for the ratio between losses to the exterior and total losses of the unconditioned zone:

\[
b_{ztu,m} = \frac{H_{ue}}{H_{ue} + H_{iu}}
\]

#### 8 Distribution Factor (F₍ztc₎ₘ)
If multiple conditioned zones exist, the distribution factor allocates transmission between them:

\[
F_{ztc,ztu,m} = \frac{H_{ztc,i,ztu,m}}{\sum_j H_{ztc,j,ztu,m}}
\]

Here it is set to `1.0` since only one conditioned zone is assumed.

---

### Example Output
```
H_ztu_tot = 78.45  # W/K
b_ztu_m = 0.63
F_ztc_ztu_m = 1.0
```

---

### Notes
- `H_ztu_tot` increases with larger areas, higher U-values, or greater ventilation exchange.  
- Default `n_ue = 0.5` corresponds to “well-sealed joints, no ventilation openings” (ISO 13789 Table 7).  
- The function currently handles **one conditioned zone**; for multiple zones, extend the `F_ztc_ztu_m` calculation.

---

