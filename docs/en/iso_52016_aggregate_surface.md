# Aggregate surface  - same direction -

Function:  `Aggregate_surfaces_by_direction(building_object)`
---

### Purpose
This function aggregates (merges) multiple building surfaces that share the **same orientation and ISO 52016 surface type** into a single, equivalent surface.  
The goal is to simplify the building model so that **heat transmission and solar radiation terms** can be computed on aggregated surfaces instead of on many small, redundant ones.

---

### Function Signature
```python
def _aggregate_surfaces_by_direction(cls, building_object)
```

### Parameters
| Name | Type | Description |
|------|------|--------------|
| `building_object` | `dict` | A dictionary-like building model that must contain a key `"building_surface"`, which is a list of surface definitions. Each surface should include ISO 52016 descriptors and physical properties (e.g., area, U-value, absorptance, etc.). |

---

### Returns
| Type | Description |
|------|--------------|
| `dict` | A shallow copy of the input `building_object`, where `building_surface` has been replaced with a **reduced list of aggregated surfaces**. |

---

### How It Works
1. **Grouping (bucketing):**  
   Surfaces are grouped by:
   - `ISO52016_type_string` (e.g., *opaque wall*, *transparent window*, etc.)
   - `ISO52016_orientation_string` (e.g., *N*, *S*, *E*, *W*, *HOR*)
   - `type` (transparent/opaque)

   → These three attributes form the **aggregation key**.

2. **Aggregation Rules:**
   - **Additive fields:**  
     - `area`  
     - `thermal_capacity`
   - **Area-weighted average fields:**  
     - `u_value`  
     - `g_value` (only for transparent surfaces)  
     - `sky_view_factor`  
     - `solar_absorptance`  
     - `convective` and `radiative` heat transfer coefficients (internal and external)
   - **Name field:**  
     The new aggregated surface name concatenates all original names (trimmed to 120 characters).

3. **Orientation Handling:**  
   A simplified numeric orientation is reattached to each aggregated surface:
   - Default: `{azimuth: 0, tilt: 90}` (vertical)
   - If `ISO52016_orientation_string == "HOR"` → `{azimuth: 0, tilt: 0}` (horizontal)

4. **Output:**  
   The method builds a new list of surfaces where each element represents one **equivalent aggregated surface** per direction and type.

---

### Aggregation Example
If the input building object contains three south-facing opaque walls:

| Surface Name | Type | ISO52016 Type | Orientation | Area (m²) | U-Value (W/m²K) |
|---------------|------|----------------|-------------|------------|-----------------|
| Wall_1 | opaque | Wall | SV | 10 | 0.30 |
| Wall_2 | opaque | Wall | SV | 15 | 0.25 |
| Wall_3 | opaque | Wall | SV | 5  | 0.40 |

After aggregation, the function returns one equivalent surface:

| New Name | Type | Orientation | Area (m²) | U-Value (W/m²K) |
|-----------|------|-------------|------------|-----------------|
| Wall_1 + Wall_2 + Wall_3 | opaque | SV | 30 | 0.30 |

where the **U-value** is computed as  

\[
U_{agg} = \frac{\sum (U_i \times A_i)}{\sum A_i}
\]

---

### Advantages
- Reduces model complexity for ISO 52016 energy balance computations.
- Speeds up simulation and simplifies reporting.
- Avoids double-counting of identical surfaces.
- Ensures consistent area-weighted physical properties.

---

### Limitations
- Works only for dictionary-style `building_object`.  
- Orientation azimuth/tilt are currently placeholders, not exact averages.
- Requires each surface to contain both:
    - `ISO52016_type_string` that is the `type`in the BUI dict
    - `ISO52016_orientation_string` that is the `orientation` in the BUI dict
    example:

    ```python
            ..{
                "name": "Roof surface",
                "type": "adj",     # <-----
                "area": 130,
                "sky_view_factor": 1.0,
                "u_value": 2.2,
                "solar_absorptance": 0.4,
                "thermal_capacity": 741500.0,
                "orientation": {   # <-----
                    "azimuth": 0,
                    "tilt": 0
                },
                "name_adj_zone": None
            }
    ```



### Example Usage
```python
building_object = ISO52016()._aggregate_surfaces_by_direction(building_object)

for surf in building_object["building_surface"]:
    print(f"{surf['ISO52016_orientation_string']} | {surf['type']} | Area = {surf['area']:.1f} m² | U = {surf['u_value']:.2f}")

```

Example output:
```
HOR | opaque | Area = 130.0 m² | U = 2.20
NV | opaque | Area = 30.0 m² | U = 1.40
SV | opaque | Area = 30.0 m² | U = 1.40
EV | opaque | Area = 30.0 m² | U = 1.20
WV | opaque | Area = 30.0 m² | U = 1.20
HOR | opaque | Area = 100.0 m² | U = 1.60
EV | transparent | Area = 4.0 m² | U = 5.00
WV | transparent | Area = 4.0 m² | U = 5.00
```

---

### Key Takeaways
- Aggregates surfaces sharing **type + ISO orientation**.
- Uses **area-weighted** averages for intensive properties.
- Returns a **clean, compact list of equivalent surfaces** .

---
