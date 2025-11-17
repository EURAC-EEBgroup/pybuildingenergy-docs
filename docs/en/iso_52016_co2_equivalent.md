# Calculation of CO₂ Equivalent (CO₂e) Emissions from an Energy Simulation

This document explains how to calculate CO₂-equivalent emissions (CO₂e) from the results of an energy simulation.  
The method aligns with **ISO 52000**, **EN 15603**, and **GHG Protocol** frameworks.

---

## 📊 Required Data from the Simulation

For each energy carrier (electricity, natural gas, biomass, district heating, etc.), you need:
- Final energy consumption (kWh, usually based on LHV)
- (Optional) Exported energy (e.g., PV or CHP generation)
- (Optional) Auxiliary information such as generator efficiencies or CHP heat/power split

---

## ⚙️ Calculation Settings

### Emission Scopes
- **Scope 1:** Direct on-site fuel combustion (boilers, CHP, etc.)
- **Scope 2:** Purchased electricity, steam, heat, or cooling
- **Scope 3 (optional):** Upstream emissions (extraction, transport, T&D losses)

### Electricity Method
- **Location-based:** Average grid emission factor (annual or time-resolved)
- **Market-based:** Supplier-specific emission factor (residual mix)

---

## 🧮 General Formula

For each energy carrier \(i\) and time step \(t\):

\[
\mathrm{CO_2e}_{i,t} = E_i(t) \times \mathrm{EF}_{i}^{comb}(t) + E_i(t) \times \mathrm{EF}_{i}^{upstream}(t)
\]

where:  
- \(E_i(t)\): energy consumption (kWh)  
- \(\mathrm{EF}_{i}^{comb}\): direct combustion emission factor (kgCO₂e/kWh)  
- \(\mathrm{EF}_{i}^{upstream}\): upstream emission factor (kgCO₂e/kWh)

If emissions are split by gas species (CO₂, CH₄, N₂O):

\[
\mathrm{CO_2e} = \mathrm{CO_2} + \mathrm{CH_4} \times \mathrm{GWP}_{100,CH_4} + \mathrm{N_2O} \times \mathrm{GWP}_{100,N_2O}
\]

---

## 🌍 Typical Emission Factors

| Energy carrier | Emission factor (kgCO₂e/kWh) | Example source |
|----------------|-------------------------------|----------------|
| Electricity (EU grid) | 0.25 | ENTSO-E 2023 |
| Natural gas (combustion) | 0.202 | IPCC 2006 |
| Natural gas (upstream) | 0.025 | DEFRA 2023 |
| Biomass (solid) | 0 (biogenic) | IPCC 2006 |

> ⚠️ Always use emission factors consistent in **region** and **year**.

---

## 🔋 Handling On-Site Generation

- **Self-consumed PV:** reduces imported grid electricity.  
- **Exported PV:** should not be subtracted from consumption unless the reporting framework allows it.  
- **CHP systems:** allocate fuel emissions between heat and power using an efficiency- or substitution-based method.

---

## 📘 Example Calculation

| Energy type | Consumption (kWh) | EF (kgCO₂e/kWh) | Emissions (kgCO₂e) |
|--------------|------------------:|----------------:|-------------------:|
| Electricity (grid) | 10,000 | 0.25 | 2,500 |
| Natural gas (comb.) | 5,000 | 0.202 | 1,010 |
| Natural gas (upstream) | 5,000 | 0.025 | 125 |
| **Total** | — | — | **3,635** |

---

## 🐍 Example Python Script

```python

import pandas as pd

# Input data (final energy in kWh)
energy = pd.Series({
    'electricity_grid': 10000,
    'natural_gas': 5000,
})

# Emission factors (kgCO2e/kWh)
EF = {
    'electricity_grid': 0.25,   # Scope 2
    'gas_combustion': 0.202,    # Scope 1
    'gas_upstream': 0.025,      # Scope 3
}

co2e = {
    'Scope2_electricity': energy['electricity_grid'] * EF['electricity_grid'],
    'Scope1_gas': energy['natural_gas'] * EF['gas_combustion'],
    'Scope3_gas_upstream': energy['natural_gas'] * EF['gas_upstream'],
}

co2e['Total'] = sum(co2e.values())
print(pd.Series(co2e).round(1))
```