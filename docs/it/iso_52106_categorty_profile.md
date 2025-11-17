## Function: `generate_category_profile()`

### Context

In building energy simulations — especially those following **ISO 52016-1:2017** (Energy needs for heating and cooling, internal temperatures, and loads) or the broader **EPB** (Energy Performance of Buildings) framework — each thermal zone requires **hourly profiles** for occupancy, lighting, appliances, ventilation, heating, and cooling.  

These profiles describe the **temporal behavior** of internal gains and system operation (e.g., when people are present, when lights are on, or when HVAC is active).  
This function automates the generation of such profiles by merging **custom schedules** (if defined within a building object) with **default type-based schedules**, ensuring every category has a valid 24-hour pattern.

The default type-based schedules are define in the file: `table_iso_16798_1.py`, where typical profile are getting from the EN ISO 16798-1 standard.

---

### Purpose

`generate_category_profile()` builds a consistent set of **hourly category profiles** (weekday/weekend) for:
- Occupancy  
- Appliances  
- Lighting  
- Ventilation  
- Heating  
- Cooling  

It ensures that all schedules are properly defined, validated, and ready for use in **energy balance, comfort, or control** simulations.

---

### Function signature
```python
generate_category_profile(
    cls,
    building_object,
    occupants_schedule_workdays,
    occupants_schedule_weekend,
    appliances_schedule_workdays,
    appliances_schedule_weekend,
    lighting_schedule_workdays,
    lighting_schedule_weekend,
)
```

---

### How it works

1. **Identify building type**  
   Extracts the `building_type_class` from the input object to determine which default schedules to use.

2. **Load or fallback for each category**  
   - For **occupants**, **appliances**, and **lighting**:  
     If custom 24-hour profiles exist in `building_object["building_parameters"]["internal_gains"]`, they are used directly.  
     Otherwise, defaults are taken from the provided schedule dictionaries.
   - For **ventilation**, **heating**, and **cooling**:  
     If no profiles are defined in the building object, they **inherit the occupancy schedule** as a fallback.

3. **Validation**  
   Ensures that every schedule contains exactly **24 hourly values** (one per hour of the day).

4. **Output assembly**  
   Returns all category profiles in a structured dictionary format.

---

### Returned structure

```python
{
    "ventilation": {"weekday": array(24), "holiday": array(24)},
    "heating":     {"weekday": array(24), "holiday": array(24)},
    "cooling":     {"weekday": array(24), "holiday": array(24)},
    "occupancy":   {"weekday": array(24), "holiday": array(24)},
    "lighting":    {"weekday": array(24), "holiday": array(24)},
    "appliances":  {"weekday": array(24), "holiday": array(24)},
}
```

Each category contains **24 hourly fractions** for weekdays and weekends (holidays), typically in the range 0–1 or as relative intensity values.

---

### Parameters

| Parameter | Type | Description |
|------------|------|-------------|
| `building_object` | `dict` | Building model containing `building_type_class` and optional internal gain profiles. |
| `occupants_schedule_workdays/weekend` | `dict[str, list[float]]` | Default hourly occupancy profiles (24 values each). |
| `appliances_schedule_workdays/weekend` | `dict[str, list[float]]` | Default hourly appliance profiles. |
| `lighting_schedule_workdays/weekend` | `dict[str, list[float]]` | Default hourly lighting profiles. |

---

### Returns
`dict` — A complete set of hourly category profiles for use in thermal simulations, HVAC control logic, or internal gain estimation.

---

### Example

```python
profiles = generate_category_profile(
    building_object=my_building,
    occupants_schedule_workdays=OCCUPANTS_WD,
    occupants_schedule_weekend=OCCUPANTS_WE,
    appliances_schedule_workdays=APPLIANCES_WD,
    appliances_schedule_weekend=APPLIANCES_WE,
    lighting_schedule_workdays=LIGHTING_WD,
    lighting_schedule_weekend=LIGHTING_WE,
)

# Example: access weekday lighting profile
lighting_profile = profiles["lighting"]["weekday"]
```

---

### Notes
- All profiles **must contain exactly 24 numeric values**.  
- Missing **ventilation**, **heating**, or **cooling** profiles automatically default to the **occupancy** profile.  
- Designed for integration with ISO 52016-1-based or EPB-based **building energy models**.  
- Works as a preprocessing step to ensure that all internal gain and system schedules are complete and consistent before running the energy balance.

---

### Integration Example

This function is typically used in the **preprocessing pipeline** before running a dynamic energy simulation:
1. Import building geometry, envelope, and system parameters.  
2. Generate category profiles using `generate_category_profile()`.  
3. Feed the resulting hourly profiles into a thermal or energy balance model.  
4. Compute heating/cooling needs and comfort metrics following ISO 52016-1.

