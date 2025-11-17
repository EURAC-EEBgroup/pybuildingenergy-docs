# Aeral Heat capacity

Function: `Areal_heat_capacity_of_element(building_object)`
---

### Purpose
Computes the **areal heat capacity allocation per node** for each building envelope element according to **EN ISO 52016-1 (6.5.7)** and Annex B tables (e.g., **B.13** classes and **B.14** capacities).  
The routine returns a 5×N matrix `kappa_pli_eli_` where:
- rows (0..4) correspond to **nodes** `kpl1..kpl5` (external → internal or per the chosen nodal scheme),
- columns (0..N-1) correspond to **envelope elements**,
- entries hold the **areal heat capacity** assigned to each node/element.

> The node distribution depends on the **construction mass class** (`class_i`, `class_e`, `class_ie`, `class_d`, `class_m`).

---

### Function Signature

```python
def Areal_heat_capacity_of_element(cls, building_object) -> aeral_heat_capacity
```

---

### Parameters

| Name | Type | Description |
|------|------|-------------|
| `building_object` | `dict` | Building model containing a list of surfaces in `building_surface` and global settings under `building`. |

---

### Required Fields

**On each surface in `building_surface`:**
- `ISO52016_type_string` — element type: `"OP"` (opaque), `"W"` (transparent), `"GR"` (ground-contact), `"ADJ"` (adjacent opaque).  
- `thermal_capacity` — **areal heat capacity** (e.g., from ISO 52016 Table B.14).

**On the building object:**
- `building.construction_class` — construction mass class from ISO 52016 Table B.13:  
  - `class_i`, `class_e`, `class_ie`, `class_d`, `class_m`.

---

### Returns

| Type | Contents |
|------|----------|
| `aeral_heat_capacity` | Wrapper carrying `kappa_pli_eli` (shape **5 × N**). Each column is an element; rows are nodes `kpl1..kpl5`. |

---

### Method Outline

1. **Collect element types and capacities**  

   - Build `el_type` from `surface["ISO52016_type_string"]`.  
   - Build `list_kappa_el` from `surface["thermal_capacity"]` (default **0** if missing).

2. **Initialize matrix**  

   ```text
   kappa_pli_eli_ : (5 × N) zeros
   rows 0..4 → nodes kpl1..kpl5
   cols 0..N → elements
   ```

3. **Distribute areal heat capacity by construction class (ISO 52016 Table B.13)**

   - **`class_i` — mass **concentrated at internal side**
      - **Opaque/Adjacent (`OP`, `ADJ`)**: `kpl5 = km_eli` (node 4); others 0.  
      - **Ground (`GR`)**: `kpl5 = 1e6` (treated as very large capacity placeholder); `kpl3=kpl4=0`.
   
   - **`class_e` — mass **concentrated at external side**
      - **Opaque/Adjacent**: `kpl1 = km_eli` (node 0).  
      - **Ground**: `kpl3 = km_eli` (node 2).

   - **`class_ie` — mass **split internal/external**
      - **Opaque/Adjacent**: `kpl1 = km_eli/2` and `kpl5 = km_eli/2`.  
      - **Ground**: `kpl1 = km_eli/2` and `kpl5 = km_eli/2`.

   - **`class_d` — mass **equally distributed**
      - **Opaque/Adjacent**: `kpl2 = kpl3 = kpl4 = km_eli/4` (nodes 1,2,3) and `kpl1 = kpl5 = km_eli/8` (nodes 0,4).  
      - **Ground**: `kpl3 = km_eli/4` (node 2) and `kpl4 = km_eli/2` (node 3); `kpl5 = km_eli/4` (node 4).

   - **`class_m` — mass **concentrated mid-layer**
      - **Opaque/Adjacent**: `kpl3 = km_eli` (node 2).  
      - **Ground**: `kpl4 = km_eli` (node 3).

4. **Return value**  
   Wrap `kappa_pli_eli_` in `aeral_heat_capacity(kappa_pli_eli=...)`.

---

### Node Indexing
The implementation uses a **5-node** scheme (rows 0..4 → `kpl1..kpl5`). The physical mapping (external↔internal) should match your solver’s convention. This function follows the same node positions as used elsewhere in your ISO 52016 implementation.

---

###  Example (pseudo)
```python
cap = Areal_heat_capacity_of_element(building_object=bui)

M = cap.kappa_pli_eli  # shape 5 × N
print(M.shape)         # e.g., (5, 12) for 12 elements
print(M[:, 0])         # node-wise capacities of the first element
```

---

### Notes
- Transparent elements (`type: "transparent"`) are **excluded** from mass allocation in several classes (as per code).  
- The **ground element** (`name: "Slab to ground"`) receives special handling: very large capacity in `class_i`, and specific node allocations in other classes.  
- If a surface lacks `thermal_capacity`, the corresponding entries remain **0**. Provide values consistent with ISO 52016 Annex B tables.  
- Returned units follow your input `thermal_capacity` convention (often **J/(m²·K)** in standards; the original docstring mentions **W/(m²·K)** — ensure consistency across the toolchain).

---

### References
- **EN ISO 52016-1** — *Energy performance of buildings — Calculation of energy needs for heating and cooling*.  
  - §6.5.7 (nodal method), Annex B (Tables **B.13** construction classes, **B.14** areal heat capacities).
