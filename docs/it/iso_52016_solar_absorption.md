# Solar absorption of bbuilding element

Function: `Solar_absorption_of_element(building_object)`
---

### Purpose
Computes the **solar absorption coefficients** for each building envelope element in accordance with **EN ISO 52016-1** solar heat gain modeling.  
The result is a **5×N matrix** `a_sol_pli_eli` assigning solar absorption values to the nodal structure of each surface.

---

### Function Signature
```python
def Solar_absorption_of_element(cls, building_object) -> solar_absorption_elements
```

---

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `building_object` | `dict` | Building data structure that contains a list of surfaces under `building_surface`. Each surface must define `ISO52016_type_string` and optical parameters (`solar_absorptance` or `g_value`). |

---

### Required Fields in `building_object["building_surface"]`
Each element in `building_surface` should include:
| Field | Description |
|--------|-------------|
| `ISO52016_type_string` | ISO 52016 element type string: <br>• `OP` – Opaque element <br>• `W` – Transparent (window) <br>• `GR` – Ground-contact <br>• `AD` or `ADJ` – Adjacent opaque element |
| `solar_absorptance` | Solar absorptance coefficient (0–1) for opaque elements. |
| `g_value` | Solar energy transmittance (0–1) for transparent elements. |

---

### Returns
| Type | Description |
|------|--------------|
| `solar_absorption_elements` | Wrapper containing the 2D array `a_sol_pli_eli` (shape 5×N), where N = number of elements in `building_surface`. |

---

### Method Overview

1. **Determine number of envelope elements**

   ```python
   el_list = len(building_object["building_surface"])
   ```
   Creates an empty coefficient list `solar_abs_elements` of length N.

2. **Extract solar properties**
   - For each surface:
      - If `"solar_absorptance"` is defined and the element is **not** `"AD"` or `"ADJ"`, use its value.
      - If `"solar_absorptance"` is missing, use the `"g_value"` (for transparent elements).
      - If the element type is `"AD"` or `"ADJ"`, set absorptance = 0.0 (no solar gain through adjacent walls).

3. **Create absorption matrix**

   ```python
   a_sol_pli_eli = np.zeros((5, el_list))
   a_sol_pli_eli[0, :] = solar_abs_elements
   ```
   Only the **first node (external surface)** receives the solar absorptance value; deeper nodes remain zero.

4. **Return result**

   ```python
   return solar_absorption_elements(a_sol_pli_eli=a_sol_pli_eli)
   ```

---

### 📊 Example

```python
inputs = {
    "type": ["GR", "OP", "OP", "OP", "OP", "OP", "W", "W", "W", "W"],
    "a_sol": [0, 0.6, 0.6, 0.6, 0.6, 0.6, 0, 0, 0, 0],
}

# Expected result:
a_sol_pli_eli = np.array([
    [0. , 0.6, 0.6, 0.6, 0.6, 0.6, 0. , 0. , 0. , 0. ],
    [0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. ],
    [0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. ],
    [0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. ],
    [0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. ],
])
```

---

### 🧩 Notes
- Only **external surfaces** (node 0) receive solar absorption values, as solar radiation is applied to the outermost layer.  
- Adjacent elements (`"AD"` or `"ADJ"`) are excluded from solar absorption (set to zero).  
- Transparent elements (`"W"`) use `g_value` instead of `solar_absorptance`.  
- The 5×N output format is consistent with the 5-node thermal network defined in **ISO 52016-1**.

---

### 📚 References
- **EN ISO 52016-1:2017** – *Energy performance of buildings – Calculation of energy needs for heating and cooling*.  
  - Section 6.5.7 – Definition of solar absorptance and its application to surface nodes.
