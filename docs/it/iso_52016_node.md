# Node of building element

The following two functions calculates the number of nodes to be used in opaque and transparent elements in the 5-node thermal network model.


## Function: `Number_of_nodes_element(building_object)`

### Purpose
Determines the **number of thermal nodes** for each building element, according to its type (opaque, transparent, or adiabatic).  
This step is part of the nodal network definition in **EN ISO 52016-1:2017**, used for energy balance and dynamic thermal simulations.

---

### Function Signature

```python
def Number_of_nodes_element(cls, building_object) -> numb_nodes_facade_elements
```

---

### Parameters

| Name | Type | Description |
|------|------|-------------|
| `building_object` | `dict` | Building model containing a list of surfaces under `building_surface`. Each element defines its physical type. |

---

### Required Fields in `building_object["building_surface"]`

| Field | Description |
|--------|-------------|
| `type` | Element type string: <br>• `"opaque"` or `"OP"` → Opaque element <br>• `"transparent"` or `"W"` → Transparent element (window) <br>• `"adiabatic"` → Internal/insulated partition with no heat flow. |

---

### Returns

| Variable | Type | Description |
|-----------|------|-------------|
| `Rn` | `int` | Index of the **last node** in the complete nodal vector. Used for vector and matrix sizing. |
| `Pln` | `np.ndarray[int]` | Array of the **number of nodes per element**: 5 for opaque, 2 for transparent, 0 for adiabatic. |
| `PlnSum` | `np.ndarray[int]` | Sequential cumulative node indices for mapping all elements. |
| `numb_nodes_facade_elements` | `object` | Wrapper containing `(Rn, Pln, PlnSum)`. |

---

### Method Overview

1. **Initialize all elements as 5-node systems**

   ```python
   el_list = len(building_object["building_surface"])
   Pln = np.full(el_list, 5)
   ```
   ISO 52016 default: each opaque surface is modeled with 5 thermal nodes.

2. **Adjust per element type**

   - Transparent (`"transparent"`) → 2 nodes (external/internal surfaces only).  
   - Adiabatic (`"adiabatic"`) → 0 nodes (no heat transfer).

   ```python
   for i, surf in enumerate(building_object["building_surface"]):
       if surf["type"] == "transparent":
           Pln[i] = 2
       elif surf["type"] == "adiabatic":
           Pln[i] = 0
   ```

3. **Compute cumulative node index (`PlnSum`)**

   ```python
   for Eli in range(1, el_list):
       PlnSum[Eli] = PlnSum[Eli-1] + Pln[Eli-1]
   ```
   Each element’s node sequence starts where the previous one ends.

4. **Compute the last node index (`Rn`)**

   ```python
   Rn = PlnSum[-1] + Pln[-1] + 1
   ```
   Adds one final node for matrix dimensioning in the solver.

5. **Return wrapper**

   ```python
   return numb_nodes_facade_elements(Rn, Pln, PlnSum)
   ```

---

### Example

```python
building_object = {
    "building_surface": [
        {"type": "opaque"},
        {"type": "transparent"},
        {"type": "opaque"},
        {"type": "adiabatic"}
    ]
}

nodes = Number_of_nodes_element(building_object)
print("Rn:", nodes.Rn)
print("Pln:", nodes.Pln)
print("PlnSum:", nodes.PlnSum)
```
Output:
```
Rn: 13
Pln: [5 2 5 0]
PlnSum: [0 5 7 12]
```

---

### Notes
- **Opaque** and **adiabatic** surfaces are both considered non-transparent; adiabatic ones simply have no conductive nodes.  
- The nodal indexing ensures continuous node numbering across all envelope elements — crucial for constructing the global heat transfer matrix.  
- ISO 52016 recommends **5 nodes** for opaque elements (multi-layer walls/roofs) and **2 nodes** for transparent elements (windows).  
- The function prepares data for the later calculation of **heat capacity**, **conductance**, and **solar absorption** matrices.

---

## Function:
`Conduttance_node_of_element(building_object, lambda_gr=2.0)`

### Purpose
Calculates the **thermal conductance** between the internal nodes (`pli` and `pli-1`) of each construction element in accordance with **EN ISO 52016-1 (Section 6.5.7)**.  
It defines the inter-nodal conductances (W/m²·K) that represent the heat transfer capability through each layer of opaque, transparent, or ground-contact elements in the 5-node thermal network model.

---

### Function Signature

```python
def Conduttance_node_of_element(cls, building_object, lambda_gr=2.0) -> conduttance_elements
```

---

###  Parameters

| Name | Type | Default | Description |
|------|------|----------|-------------|
| `building_object` | `dict` | — | Building structure containing the envelope elements in `building_surface`. |
| `lambda_gr` | `float` | `2.0` | Ground thermal conductivity (W/m·K), used for ground-contact elements (`GR`). |

---

###  Required Fields in `building_object["building_surface"]`

!!! Note
    The type of the surface has been mapped in the calculation using the following code:

    - `OP`: Opaque element
    - `W`: Transparent element
    - `GR`: Ground-contact element
    - `AD`: Adiabatic element
    - `ADJ`: Adjacent element

    ```python
    ...
    for i, surf in enumerate(building_object["building_surface"]):
        if surf["type"] == "opaque":
            if surf["sky_view_factor"] == 0:
                typology_elements[i] = "GR"
            else:
                typology_elements[i] = "OP"
        elif surf["type"] == "adiabatic":
            typology_elements[i] = "AD"
        elif surf["type"] == "transparent":
            typology_elements[i] = "W"
        elif surf["type"] == "adjacent":
            typology_elements[i] = "ADJ"
        surf["ISO52016_type_string"] = typology_elements[i]
    ```


Each surface element must include:

| Field | Description |
|--------|-------------|
| `ISO52016_type_string` | ISO 52016 element type string: <br>• `OP` = Opaque element <br>• `W` = Transparent (window) <br>• `GR` = Ground-contact <br>• `AD` or `ADJ` = Adjacent wall |
| `u_value` | Overall thermal transmittance (W/m²·K). |
| `convective_heat_transfer_coefficient_internal` | Internal convective heat transfer coefficient (W/m²·K). |
| `radiative_heat_transfer_coefficient_internal` | Internal radiative heat transfer coefficient (W/m²·K). |
| `area` | Element surface area (m²). |
| *(optional)* `convective_heat_transfer_coefficient_external` | If not defined, default = **20 W/m²·K** (ISO 13789). |
| *(optional)* `radiative_heat_transfer_coefficient_external` | If not defined, default = **4.14 W/m²·K** (ISO 13789). |

---

### Returns

| Type | Description |
|------|--------------|
| `conduttance_elements` | Wrapper object containing the matrix `h_pli_eli` (4×N) where N = number of envelope elements. Each row corresponds to a node pair (`pli`, `pli−1`) and each column to an element. Units: **W/m²·K**. |

---

###  Method Overview

1. **Initialize constants and arrays**
    - Ground resistance:  
    
    \[ R_{gr} = \frac{0.5}{\lambda_{gr}} \;(\text{m}^2K/W) \]
   
   - Build lists of:
    - element types (`el_type`),  
    - U-values,  
    - internal heat-transfer coefficients (`h_ci`, `h_ri`),  
    - external coefficients (`h_ce`, `h_re`).

2. **Assign external coefficients**
   
   - Default convective = **20 W/m²·K**, radiative = **4.14 W/m²·K**.  
   - For *adjacent* elements (`AD`), both coefficients are set to 0 → no external exchange.

3. **Compute construction resistance**  
   
    \[R_{c,eli} = \frac{1}{U_{eli}} - \frac{1}{(h_{ci}+h_{ri})} - \frac{1}{(h_{ce}+h_{re})}\]
   
    This represents the **core conduction resistance** of the element (m²·K/W).

4. **Distribute conductances among layers**  
   
   For each element *i*, the nodal conductances `h_pli_eli[layer, i]` are defined as:

   **Layer 1 (node pair 1–2)**

   | Type | Formula |
   |-------|----------|
   | `OP`, `ADJ` | \( h = 6/R_c \) |
   | `W` | \( h = 1/R_c \) |
   | `GR` | \( h = 2/R_{gr} \) |

   **Layer 2 (node pair 2–3)**

   | Type | Formula |
   |-------|----------|
   | `OP`, `ADJ` | \( h = 3/R_c \) |
   | `GR` | \( h = 1/(R_c/4 + R_{gr}/2) \) |

   **Layer 3 (node pair 3–4)**

   | Type | Formula |
   |-------|----------|
   | `OP`, `ADJ` | \( h = 3/R_c \) |
   | `GR` | \( h = 2/R_c \) |

   **Layer 4 (node pair 4–5)**

   | Type | Formula |
   |-------|----------|
   | `OP`, `ADJ` | \( h = 6/R_c \) |
   | `GR` | \( h = 4/R_c \) |

5. **Return**
   The final 4×N matrix is wrapped in `conduttance_elements(h_pli_eli=h_pli_eli)`.

---

### Notes

- For *adjacent* surfaces (`AD`), external heat-transfer coefficients are zero (no external exchange).  
- Ground-contact elements use simplified analytical correlations (ISO 13370).  
- `R_c` is set to ∞ for “AD” elements → conductance = 0.  
- Default coefficients (20 W/m²·K, 4.14 W/m²·K) are consistent with **ISO 13789** recommendations.  
- The 4 layers correspond to the 5-node surface temperature network used in ISO 52016.  

---

### Example

```python
h = Conduttance_node_of_element(building_object=bui, lambda_gr=2.0)
H = h.h_pli_eli
print(H.shape)  # (4, N)
print(H[:, 0])  # conductance values for element #0
```

---

### References

- **EN ISO 52016-1:2017** – *Energy performance of buildings — Calculation of energy needs for heating and cooling*, Section 6.5.7.  
- **EN ISO 13789:2017** – *Thermal performance of buildings — Transmission and ventilation heat transfer coefficients — Calculation method*.  
- **EN ISO 13370:2017** – *Heat transfer via the ground — Calculation methods* (for ground-related resistances).
