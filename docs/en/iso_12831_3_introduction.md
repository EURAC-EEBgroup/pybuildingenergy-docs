# Domestic Hot Water (DHW) Calculation — Module Overview & API Docs

*Calculation of DHW needs according to ISO 12831-3:2018.*  

The goal is to evaluate and demonstrate the validity of the DHW calculation proposed by the EN ISO 12831-3:2018.  
This work **does not replace the standard**; it is meant to be used **along with the EPB standards**.


## <h2 style="color:#df1b12; margin-bottom:0px; font-weight:bold"><strong>Introduction</strong></h2>

This module provides reference implementations to estimate **daily, monthly, and yearly** DHW **volume** and **energy** needs for buildings, following the logic and parameters in ISO 12831-3 and related EPB standards.  
It includes:

- A robust **calendar generator** based on [workalendar], to classify days as `Working`, `Non-Working`, or `Holiday`.
- Core routines to compute **DHW volume** and **thermal energy** at delivery temperature, handling multiple building usage types (residential, accommodation, healthcare, catering, hotels, sport facilities, …).
- Utility functions (e.g., month day counts) and correlations to determine **equivalent persons** and daily volume references for dwellings.

The API is meant to be **clear, testable**, and easily integrable into larger pipelines (e.g., hourly profiles, M&V checks, dashboards).  
The module relies on a set of **tabular inputs** (EPB tables B_3, B_4, B_5) and **physical constants** provided by `pybuildingenergy`.

---


## <h2 style="color:#df1b12; margin-bottom:0px; font-weight:bold"><strong>Data & External Dependencies</strong></h2>

- `table_B_3`, `table_B_4`, `table_B_5_modified`  
  DataFrames providing reference values from EPB tables:
  - **B_3**: usage types and energy/area or per-unit intensities
  - **B_4**: activity types and daily volume per functional unit
  - **B_5 (modified)**: residential typologies and liters/person/day
- `WATER_DENSITY`, `WATER_SPECIFIC_HEAT_CAPACITY`  
  Physical constants imported from `pybuildingenergy.global_inputs`.
- **Workalendar** (external): provides country calendars and `is_working_day` / `holidays(year)`.

> ⚠️ Ensure these tables/inputs are loaded in your environment before calling the main routines.

---
