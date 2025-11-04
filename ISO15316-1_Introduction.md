# Introduction to ISO 15316-1 / EN 15316-1

## Overview
**ISO 15316-1** (equivalent to **EN 15316-1** in Europe) defines the **framework and general principles** for calculating the **energy performance of building heating and domestic hot water systems**.  
It provides a **systematic, modular approach** that allows engineers, researchers, and software tools to evaluate and compare energy efficiency across different system configurations.

This standard is part of the broader *Energy Performance of Buildings (EPB)* suite developed under the **EU Energy Performance of Buildings Directive (EPBD)**.

---

## Scope
The standard covers **water-based heating and DHW systems** where heat is generated, distributed, and emitted to maintain indoor comfort.  
It applies to:
- **Emission systems** (radiators, floor heating, fan coils, etc.)
- **Distribution systems** (piping, manifolds, circulation)
- **Storage components** (thermal buffers, DHW tanks)
- **Generation systems** (boilers, heat pumps, cogeneration)

It does **not** include ventilation-only or purely air-based systems, except when heated by water circuits.

---

## Methodological Structure
EN 15316-1 introduces a **modular structure**, dividing the entire heating system into interconnected subsystems:

1. **Emission (C.2–C.5)** – heat transfer from water to the indoor space  
2. **Distribution** – transport of heat through pipes, including losses and auxiliaries  
3. **Storage** – intermediate energy buffering or recovery  
4. **Generation** – production of useful heat from a fuel or electricity source  

Each module has its own energy balance:
\[
\text{Energy In} = \text{Useful Output} + \text{Losses} - \text{Recoverable Losses} - \text{Auxiliaries}
\]

The calculation proceeds in the direction:
\[
\text{Energy Needs (Building)} \rightarrow \text{Delivered Heat (Emission)} \rightarrow \text{Distribution} \rightarrow \text{Generation} \rightarrow \text{Primary Energy Input}
\]

This enables transparent energy tracking and consistent efficiency assessment across technologies.

---

## Objectives
The main objectives of ISO 15316-1 are to:
- Provide a **consistent calculation structure** for all sub-systems in heating and DHW installations.  
- Define **input and output data** exchange between modules.  
- Enable **comparability** between different system types (e.g., boilers vs. heat pumps).  
- Serve as the **reference method** for EPB-compliant national calculation procedures.

---

## Key Principles
- **System boundary definition** – explicit separation of emission, distribution, storage, and generation.  
- **Energy flow consistency** – all sub-systems connect via clear input/output relationships.  
- **Recoverable vs. non-recoverable losses** – internal gains can offset building demand.  
- **Auxiliary energy** – electric or mechanical support energy is always accounted for.  
- **Adaptability** – compatible with both monthly and hourly calculation time steps.

---

## Benefits
- Harmonized methodology for **energy performance certificates**, design tools, and research.  
- Facilitates **diagnostic comparison** of subsystems (e.g., identifying excessive distribution losses).  
- Supports **policy implementation** under EPBD and national building codes.  
- Enhances reproducibility and transparency in **simulation and benchmarking**.

---

## Relationship with Subsequent Parts
Part 1 provides the **general framework** only.  
Detailed formulas and reference values for each sub-system are defined in:
- **EN 15316-2** – Generation systems  
- **EN 15316-3** – Distribution systems  
- **EN 15316-4** – Emission systems  
- **EN 15316-5** – Control and auxiliary energy  
- **EN 15316-6** – Domestic hot water systems

---

## References
- **EN 15316-1:2017** – *Energy performance of buildings — Method for calculation of system energy requirements and system efficiencies — Part 1: General and energy performance expression.*  
- **REHVA (2017)** — *Information Paper: CEN Standards for Heating and Domestic Hot Water Systems.*  
- **CENSE Project (EU)** — *Application of the EPBD Calculation Framework.*
