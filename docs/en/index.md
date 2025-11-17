

<figure align="center">
  <img src="../assets/images/Logo_pyBuild.png" alt="pybuildingnergy" width="200px">
</figure>

Please cite us if you use this library: 
[![DOI](https://zenodo.org/badge/761715706.svg)](https://zenodo.org/doi/10.5281/zenodo.10887919)
---

<h1 style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #003366;">
  Introduction: EPBD Requirements for ISO EN 52000 and ISO EN 15316 Standards
</h1>

<div style="border-left: 4px solid #D30000; padding: 10px; margin: 10px 0;">
<strong>Note:</strong> 
!!! New version available !!!
New features: 
- Calculation of multizona considering adiabiatic walls between zones with the same use destination
- Calculation with non heated zones 
- 

</div>


## ISO EN 52000 - Overarching Standards

The EPBD Directive 2018 (and confirmed in the 2024 revision) requires Member States to describe their national calculation methodology following the national annexes of the "overarching" standards, namely: ISO EN 52000-1, 52003-1, 52010-1, 52016-1, and 52018-1, developed under mandate M/480 given to CEN (European Committee for Standardization).

**Important**: This provision does not constitute mandatory legal codification of these standards. However, the obligation to describe the national methodology following the annexes of the overarching standards will push Member States to explain where and why they deviate from these standards, leading to greater recognition and promotion of the EPB standards set.

The ISO EN 52000 overarching standards are:

1. **ISO EN 52000-1**: General framework and procedures for EPB assessment
2. **ISO EN 52003-1**: Indicators, requirements, ratings and certificates
3. **ISO EN 52010-1**: Internal environmental parameters
4. **ISO EN 52016-1**: Internal temperatures and energy needs for heating/cooling
5. **ISO EN 52018-1**: Indicators for overall energy performance

## New EPBD Recast Methodology

The new EPBD recast provides an update on building performance assessment through a methodology that must consider various factors such as the building’s thermal characteristics, the use of renewable energy sources, building automation and control systems, ventilation, cooling, energy recovery, etc. The methodology should represent actual operating conditions, use measured energy for accuracy and comparability, and be based on hourly or sub-hourly intervals to account for variable conditions significantly impacting system performance, including internal conditions.

The energy performance of a building shall be expressed by a numeric indicator of primary energy use per unit of reference floor area per year, in kWh/(m².y), for energy performance certification and compliance with minimum energy performance requirements. Numeric indicators of final energy use per unit of reference floor area per year, in kWh/(m².y), and energy needs according to ISO EN 52000 in kWh/(m².y) shall also be used. The applied methodology for determining energy performance must be transparent, open to innovation, and reflect best practices, particularly from additional indicators.

Member States shall describe their national calculation methodology based on Annex A of the key European standards on energy performance of buildings.

## EN 15316 - Heating and Cooling Systems

The EN 15316 series covers the calculation method for system energy requirements and system efficiencies. This family of standards is an integral part of the EPB set and covers:

### EN 15316 Modular Structure:

- **EN 15316-1**: General and expression of energy performance (Modules M3-1, M3-4, M3-9, M8-1, M8-4)
- **EN 15316-2**: Emission systems (heating and cooling)
- **EN 15316-3**: Distribution systems (DHW, heating, cooling)
- **EN 15316-4-X**: Heat generation systems:
    - 4-1: Combustion boilers
    - 4-2: Heat pumps
    - 4-3: Solar thermal and photovoltaic systems
    - 4-4: Cogeneration systems
    - 4-5: District heating
    - 4-7: Biomass
- **EN 15316-5**: Storage systems

For space heating, applicable standards include EN 15316-1, EN 15316-2-1, EN 15316-2-3 and the appropriate parts of EN 15316-4 depending on the system type, including losses and control aspects.

## Relationship between EPBD 2024 and Standards

The most recent revision of the EPBD was published in May 2024, further strengthening requirements and aligning with the EU's climate neutrality objectives. Member States are encouraged to consider applicable standards, particularly from the EPB standards list.

17 of approximately 50 EPB standards are already ISO EN standards, resulting from collaboration between CEN and ISO. The other EPB standards are currently only available at the European level (CEN standards).


## pyBuildingEnergy: the python library for building performance assessment

**pyBuildingEnergy** aims to provide an assessment of building performance both in terms of energy and comfort. In this initial release, it is possible to assess the energy performance of the building using ISO EN 52106-1:2018. Additional modules will be added for a more comprehensive evaluation of performance, assessing ventilation, renewable energies, systems, etc.
The actual calculation methods for the assessment of building performance are the following:

- [x] the (sensible) energy need for heating and cooling, based on hourly or monthly calculations;

- [ ] the latent energy need for (de-)humidification, based on hourly or monthly calculations;

- [x] the internal temperature, based on hourly calculations;

- [x] the sensible heating and cooling load, based on hourly calculations;

- [ ] the moisture and latent heat load for (de-)humidification, based on hourly calculations;

- [ ] the design sensible heating or cooling load and design latent heat load using an hourly calculation interval;

- [ ] the conditions of the supply air to provide the necessary humidification and dehumidification.

The calculation methods can be used for residential or non-residential buildings, or a part of it, referred to as "the building" or the "assessed object".
ISO EN 52016-1:2018 also contains specifications for the assessment of thermal zones in the building or in the part of a building. The calculations are performed per thermal zone. In the calculations, the thermal zones can be assumed to be thermally coupled or not.
ISO EN 52016-1:2018 is applicable to buildings at the design stage, to new buildings after construction and to existing buildings in the use phase

### Weather Data

The tool can use wather data coming from 2 main sources:

- pvgis api (https://re.jrc.ec.europa.eu/pvg_tools/en/) - PHOTOVOLTAIC GEOGRAPHICAL INFORMATION SYSTEM
- .epw file from https://www.ladybug.tools/epwmap/

More details in the example folder

### Domestic Hot Water - DHW

- [x] Calculation of volume and energy need for domestic hot water according to ISO EN 12831-3. 
- [] Assessment of thermal load based on the type of DHW system

### Primary energy for heating
- [x] Calculation of primary energy for heating according to ISO EN 15316-1:2018


### Limitations

The library is developed with the intent of demonstrating specific elements of calculation procedures in the relevant standards. It is not intended to replace the regulations but to complement them, as the latter are essential for understanding the calculation. 
This library is meant to be used for demonstration and testing purposes and is therefore provided as open source, without protection against misuse or inappropriate use.

The information and views set out in this document are those of the authors and do not necessarily reflect the official opinion of the European Union. Neither the European Union institutions and bodies nor any person acting on their behalf may be held responsible for the use that may be made of the information contained herein.

### Getting Started

The following command will install the latest pyBuildinEnergy library

```bash
    pip install pybuildingenergy
```

The tool allows you to evaluate the performance of buildings in different ways: 


### Building Inputs

- for building inputs refer to `Building Inputs`: <https://eurac-eebgroup.github.io/pybuildingenergy-docs/iso_52016_input/>
- for heating system input (ISO EN 15316-1) refer to `Heating System Input`: <https://eurac-eebgroup.github.io/pybuildingenergy-docs/iso_15316_input/>

### Documentation
--------------
Check our new documentation here:https://eurac-eebgroup.github.io/pybuildingenergy-docs/

### Example

Here some `Examples <https://github.com/EURAC-EEBgroup/pyBuildingEnergy/tree/master/examples>` on pybuildingenergy application.
For more information
.....
  
### Contributing and Support

**Bug reports/Questions**
If you encounter a bug, kindly create a GitLab issue detailing the bug. 
Please provide steps to reproduce the issue and ideally, include a snippet of code that triggers the bug. 
If the bug results in an error, include the traceback. If it leads to unexpected behavior, specify the expected behavior.

**Code contributions**
We welcome and deeply appreciate contributions! Every contribution, no matter how small, makes a difference. Click here to find out more about contributing to the project.

## Acknowledgment

This work was carried out within European projects: 
Infinite - This project has received funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement No 958397, 
Moderate - Horizon Europe research and innovation programme under grant agreement No 101069834, 
with the aim of contributing to the development of open products useful for defining plausible scenarios for the decarbonization of the built environment

Reagrding the DHW Calculation: 
The work was developed using the regulations and results obtained from the spreadsheet created by the EPBCenter.

## References

1. **EPB Center** - The Energy Performance of Buildings Directive (EPBD)  
   https://epb.center/epb-standards/the-energy-performance-of-buildings-directive-epbd/
2. **REHVA Journal** - "The new EN ISO 52000 family of standards to assess the energy performance of buildings put in practice"  
   https://www.rehva.eu/rehva-journal/chapter/the-new-en-iso-52000-family-of-standards-to-assess-the-energy-performance-of-buildings-put-in-practice
3. **European Commission** - Energy Performance of Buildings Directive  
   https://energy.ec.europa.eu/topics/energy-efficiency/energy-performance-buildings/energy-performance-buildings-directive_en
4. **Directive (EU) 2024/1275** - Official text published in the Official Journal of the EU on May 8, 2024
5. **ISO EN 52010-1:2018** - Energy performance of buildings - External climatic conditions - Part 1: Conversion of climatic data for energy calculations
6. **ISO EN 52016-1:2018** - Energy performance of buildings - Energy needs for heating and cooling, internal temperatures and sensible and latent heat loads 
7. **ISO EN 12831-3:2018** - Energy performance of buildings - Method for calculation of the design heat load - Part 3: Domestic hot water systems heat load and characterisation of needs, Module M8-2, M8-3
8. **ISO EN 15316-1:2018** - Energy performance of buildings – Method for calculation of system energy requirements and system efficiencies – Part 1: General and Energy performance expression, Module M3–1, M3–4, M3–9, M8–1
9. **ISO EN 16798-7**  - Energy performance of buildings – Ventilation for buildings – Part 7: Calculation methods for the determination of air flow rates in buildings including infiltration (Module M5–5)
10. **ISO EN 16798-1** - Energy performance of buildings — Ventilation of buildings — Part 1: Indoor environmental input parameters for design and assessment of energy performance of buildings addressing indoor air quality, thermal environment, lighting and acoustics (Module M1–6)
11. **Directive (EU) 2024/1275** - Official text published in the Official Journal of the EU on May 8, 2024

## Authors: 
Daniele Antonucci, Ulrich Filippi Oberegger

## **License**:

**Version**: 0.2
**Maintainer**: Daniele Antonucci