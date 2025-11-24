
---
<figure align="center">
  <img src="assets/images/Logo_pyBuild.png" alt="pybuildingenergy" width="400px">
</figure>
---


*Citaci se usi questo library*: 
[![DOI](https://zenodo.org/badge/761715706.svg)](https://zenodo.org/doi/10.5281/zenodo.10887919)
---


<h1 style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #df1b12;">
    Introduzione: Requisiti EPBD per le norme ISO EN 52000 e EN 15316
</h1>

<div style="border-left: 4px solid #D30000; padding: 10px; margin: 10px 0;">
<strong>Note:</strong> 
!!! Nuova versione disponibile !!!
Nuove funzionalità: 
- Calcolo di multizona considerando muri adiabatici tra zone con lo stesso scopo di utilizzo
- Calcolo con zone non calde 
- 

</div>


### **ISO EN 52000 - Norme di riferimento**

La Direttiva EPBD 2018 (e confermata dalla revisione 2024) richiede ai paesi membri di descrivere la loro metodologia di calcolo nazionale seguendo le annexe nazionali delle "norme di riferimento", cioè: ISO EN 52000-1, 52003-1, 52010-1, 52016-1, e 52018-1, sviluppate sotto il mandato M/480 assegnato al CEN (Commissione Europea per lo Standardizzazione).

**Importante**: Questa disposizione non costituisce una codifica legale obbligatoria di queste norme. Tuttavia, l'obbligo di descrivere la metodologia nazionale seguendo le annexe delle norme di riferimento spingerà i paesi membri a spiegare dove e perché si deviano da queste norme, portando a una maggiore riconoscibilità e promozione del set di norme EPB.

Le norme di riferimento ISO EN 52000 sono:

1. **ISO EN 52000-1**: Struttura generale e procedure per l'analisi del performance energetico
2. **ISO EN 52003-1**: Indicatori, requisiti, valutazioni e certificati
3. **ISO EN 52010-1**: Parametri ambientali interni
4. **ISO EN 52016-1**: Temperature interne e energia necessaria per il calore/aria condizionata
5. **ISO EN 52018-1**: Indicatori per il performance energetico globale

### **Nuova metodologia per la valutazione del performance energetico**

La nuova revisione del EPBD offre un aggiornamento sulla valutazione del performance energetico attraverso una metodologia che deve considerare vari fattori come le caratteristiche termiche del edificio, l'uso di fonti di energia rinnovabile, i sistemi di automazione e controllo del edificio, ventilazione, raffreddamento, recupero energetico, ecc. La metodologia deve rappresentare le condizioni di operazione effettive, utilizzare l'energia misurata per la precisione e la comparabilità, e essere basata su intervalli orari o sub-orari per conto delle condizioni variabili che influenzano significativamente le prestazioni dei sistemi, inclusi i parametri interni.

L'energia del edificio deve essere espressa da un indicatore numerico di energia primaria utilizzata per unità di superficie di riferimento al mese, in kWh/(m².y), per la certificazione del performance energetico e la conformità ai requisiti di performance energetica minima. Gli indicatori numerici di energia finale per unità di superficie di riferimento al mese, in kWh/(m².y), e le necessità energetiche secondo ISO EN 52000 in kWh/(m².y) devono essere utilizzati anche. La metodologia applicata per determinare il performance energetico deve essere trasparente, aperta all'innovazione e riflettere le migliori pratiche, in particolare dagli indicatori aggiuntivi.

I paesi membri devono descrivere la loro metodologia di calcolo nazionale basata sull'Annex A delle norme europee chiave per il performance energetico degli edifici.

### **EN 15316 - Sistemi di calore**

La serie EN 15316 copre il metodo di calcolo per le necessità energetiche e le efficacità dei sistemi. Questa famiglia di norme è una parte integrante del set EPB e copre:

### **Struttura modulare EN 15316:**

- **EN 15316-1**: Struttura generale e espressione del performance energetico (Moduli M3-1, M3-4, M3-9, M8-1, M8-4)
- **EN 15316-2**: Sistemi di emissione (calore e aria condizionata)
- **EN 15316-3**: Sistemi di distribuzione (acqua calda, calore, aria condizionata)
- **EN 15316-4-X**: Sistemi di generazione di calore:
    - 4-1: Bollenti a combustione
    - 4-2: Caldaie a pompe di calore
    - 4-3: Solar thermal and photovoltaic systems
    - 4-4: Cogeneration systems
    - 4-5: District heating
    - 4-7: Biomass
- **EN 15316-5**: Sistemi di storage

Per il calcolo del calore spaziale, le norme applicabili includono EN 15316-1, EN 15316-2-1, EN 15316-2-3 e le parti appropriate di EN 15316-4 a seconda del tipo di sistema, includendo le perdite e gli aspetti di controllo.

### **Relazione tra EPBD 2024 e le norme**

La revisione più recente del EPBD è stata pubblicata in maggio 2024, ulteriormente consolidando i requisiti e allineandosi con gli obiettivi di neutralità climatica dell'UE. I paesi membri sono incoraggiati a considerare le norme applicabili, in particolare dalla lista delle norme EPB.

17 di circa 50 norme EPB sono già norme EN ISO, risultanti dalla collaborazione tra CEN e ISO. Le altre norme EPB sono attualmente disponibili solo a livello europeo (norme CEN).


### **pyBuildingEnergy: la libreria python per l'analisi del performance energetico**

**pyBuildingEnergy** ha lo scopo di fornire un'analisi del performance energetico sia in termini di energia che di comfort. In questa versione iniziale, è possibile valutare il performance energetico dell'edificio utilizzando ISO EN 52106-1:2018, EN ISO 52010-1:2018, EN 15316-1:2018, EN 16798-1:2018, EN 16798-7:2018, etc.. Additional modules will be added for a more comprehensive evaluation of performance, assessing ventilation, renewable energies, HVAC systems, etc.
I metodi di calcolo attualmente disponibili per l'analisi del performance energetico sono i seguenti:

- [x] Calore sensibile (sensible) per  riscaldamento e raffrescamento, con calcolo orario e mensile; 
- [ ] the latent energy need for (de-)humidification, based on hourly or monthly calculations;
- [x] the internal temperature, based on hourly calculations;
- [x] the sensible heating and cooling load, based on hourly calculations;

- [ ] the moisture and latent heat load for (de-)humidification, based on hourly calculations;

- [ ] the design sensible heating or cooling load and design latent heat load using an hourly calculation interval;

- [ ] the conditions of the supply air to provide the necessary humidification and dehumidification.

The calculation methods can be used for residential or non-residential buildings, or a part of it, referred to as "the building" or the "assessed object".
ISO EN 52016-1:2018 also contains specifications for the assessment of thermal zones in the building or in the part of a building. The calculations are performed per thermal zone. In the calculations, the thermal zones can be assumed to be thermally coupled or not.
ISO EN 52016-1:2018 is applicable to buildings at the design stage, to new buildings after construction and to existing buildings in the use phase

### **Weather Data**

The tool can use wather data coming from 2 main sources:

- pvgis api (https://re.jrc.ec.europa.eu/pvg_tools/en/) - PHOTOVOLTAIC GEOGRAPHICAL INFORMATION SYSTEM
- .epw file from https://www.ladybug.tools/epwmap/

More details in the example folder

### **Domestic Hot Water - DHW**

- [x] Calculation of volume and energy need for domestic hot water according to EN 12831-3. 
- [] Assessment of thermal load based on the type of DHW system

### **Primary energy for heating**
- [x] Calculation of primary energy for heating according to EN 15316-1:2018


### **Limitations**

The library is developed with the intent of demonstrating specific elements of calculation procedures in the relevant standards. It is not intended to replace the regulations but to complement them, as the latter are essential for understanding the calculation. 
This library is meant to be used for demonstration and testing purposes and is therefore provided as open source, without protection against misuse or inappropriate use.

The information and views set out in this document are those of the authors and do not necessarily reflect the official opinion of the European Union. Neither the European Union institutions and bodies nor any person acting on their behalf may be held responsible for the use that may be made of the information contained herein.

### **Getting Started**

The following command will install the latest pyBuildinEnergy library

```bash
    pip install pybuildingenergy
```

The tool allows you to evaluate the performance of buildings in different ways: 


### **Building Inputs**

- for building inputs refer to `Building Inputs`: <https://eurac-eebgroup.github.io/pybuildingenergy-docs/iso_52016_input/>
- for heating system input (EN 15316-1) refer to `Heating System Input`: <https://eurac-eebgroup.github.io/pybuildingenergy-docs/iso_15316_input/>

### **Documentation**
--------------
Check our new documentation here: `Documentation <https://eurac-eebgroup.github.io/pybuildingenergy-docs/>`

### **Example**

Here some `Examples <https://github.com/EURAC-EEBgroup/pyBuildingEnergy/tree/master/examples>` on pybuildingenergy application.
For more information
.....
  
### **Contributing and Support**

**Bug reports/Questions**
If you encounter a bug, kindly create a GitLab issue detailing the bug. 
Please provide steps to reproduce the issue and ideally, include a snippet of code that triggers the bug. 
If the bug results in an error, include the traceback. If it leads to unexpected behavior, specify the expected behavior.

**Code contributions**
We welcome and deeply appreciate contributions! Every contribution, no matter how small, makes a difference. Click here to find out more about contributing to the project.



## <h2 style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #df1b12;">Acknowledgment</h2>


This work was carried out within European projects: 
Infinite - This project has received funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement No 958397, 
Moderate - Horizon Europe research and innovation programme under grant agreement No 101069834, 
with the aim of contributing to the development of open products useful for defining plausible scenarios for the decarbonization of the built environment

Reagrding the DHW Calculation: 
The work was developed using the regulations and results obtained from the spreadsheet created by the EPBCenter.


## <h2 style="font-family: 'Segoe UI', TTahoma, Geneva, Verdana, sans-serif; color: #df1b12;">References</h2>

1. **EPB Center** - The Energy Performance of Buildings Directive (EPBD)  
   https://epb.center/epb-standards/the-energy-performance-of-buildings-directive-epbd/
2. **REHVA Journal** - "The new EN ISO 52000 family of standards to assess the energy performance of buildings put in practice"  
   https://www.rehva.eu/rehva-journal/chapter/the-new-en-iso-52000-family-of-standards-to-assess-the-energy-performance-of-buildings-put-in-practice
3. **European Commission** - Energy Performance of Buildings Directive  
   https://energy.ec.europa.eu/topics/energy-efficiency/energy-performance-buildings/energy-performance-buildings-directive_en
4. **Directive (EU) 2024/1275** - Official text published in the Official Journal of the EU on May 8, 2024
5. **ISO EN 52010-1:2018** - Energy performance of buildings - External climatic conditions - Part 1: Conversion of climatic data for energy calculations
6. **ISO EN 52016-1:2018** - Energy performance of buildings - Energy needs for heating and cooling, internal temperatures and sensible and latent heat loads 
7. **EN 12831-3:2018** - Energy performance of buildings - Method for calculation of the design heat load - Part 3: Domestic hot water systems heat load and characterisation of needs, Module M8-2, M8-3
8. **EN 15316-1:2018** - Energy performance of buildings – Method for calculation of system energy requirements and system efficiencies – Part 1: General and Energy performance expression, Module M3–1, M3–4, M3–9, M8–1
9. **EN 16798-7**  - Energy performance of buildings – Ventilation for buildings – Part 7: Calculation methods for the determination of air flow rates in buildings including infiltration (Module M5–5)
10. **EN 16798-1** - Energy performance of buildings — Ventilation of buildings — Part 1: Indoor environmental input parameters for design and assessment of energy performance of buildings addressing indoor air quality, thermal environment, lighting and acoustics (Module M1–6)
11. **Directive (EU) 2024/1275** - Official text published in the Official Journal of the EU on May 8, 2024

## <h2 style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #df1b12;">Authors</h2>
- [**Daniele Antonucci**](https://www.eurac.edu/en/people/daniele-antonucci)
- [**Ulrich Filippi Oberegger**](https://www.eurac.edu/en/people/ulrich-filippi)

## <h2 style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #df1b12;">License</h2>
BSD 3-Clause License

## <h2 style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #df1b12;">Version</h2>
0.2

## <h2 style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #df1b12;">Maintainer</h2>
Daniele Antonucci