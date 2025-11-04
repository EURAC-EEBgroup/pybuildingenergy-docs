# Heating circuit.


The library provides modules for evaluating 4 types of hydraulic circuits, where, based on Table C.1 of the standard, for each circuit it is identified which type of emission system to use and the type of control. as defined below: 

| Code| Module | Emitters | Control |
|-----|--------|----------|---------|
| C2  | Constan mass flow rate and varying water temperature | Radiators and Panels| Heating curve, mixing valvew and variable generation temperature | 
| C3  | Varying mass flow (constant temperature) | Radiators, Panels, Heating coils| Thermostatic valve, flow rate control with two way valve | 
| C4  | ON-OFF and varying temperature | Radiators and Panels| On-Off control| 
| C5  | Varying heat exchange | Fan-coil, heating coils| emitters with on-off blower  and continuos circulation 3 way by-pass valve control|


All modules allow the us of a mixing valve to allow different temperatures in the different circuits. A distinction is made between: 
- the emitter tmperature and flow rate;
- the circuit temperature and flow rate; 

They differ where there is a mixing or by-pass 3 way valve in the circuit.

## C2 - constant mass flow rate and varying water temperature

<p align="center">
  <img src="https://github.com/EURAC-EEBgroup/pybuildingenergy-docs/blob/main/images/system_c2.jpg" alt="BrickLLM" style="width: 100%;">
  <!-- <img src="https://raw.githubusercontent.com/EURAC-EEBgroup/brick-llm/refs/heads/main/docs/assets/brickllm_banner.png" alt="BrickLLM" style="width: 100%;"> -->
</p>    
