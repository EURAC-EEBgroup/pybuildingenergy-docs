# ISO 52016 Input Check

The data provided before being used for the simulation are processed and evaluated to be considered fit for the simulation. This process includes a series of checks that allow to identify any potential errors. 
The following controls are applied:

# Thermal and Adjacent Zone
Uno degli errori più caratteristici può essere quello di immetere dei valori errati di superficie della parete di confine tra la zona termica e la zona non termica. Un esempio è quello di dare dei valori più alti della superificie della parete nella zona non termica rispetto alla superificie della parete nella zona termica. In questo caso se il controllo risulta essere negativo allora il tool imposta il valore del superificie della zona non termica uguale a quello della zona termica. 
Qui voglio dire che sebbene la superficie di contatto è la stessa pu`o succedere che la parete della zona termica sia o totlamente a contatto con la zon non termica o solamente una parte a contatto con la zona termica   


# Quality check of system inputs:

### `check_heating_system_inputs` Function

This function validates and normalizes the input configuration for the heating system. It performs the following checks:

1. **TB14 Table**: 
   - If a custom `TB14` DataFrame is provided, it is used.
   - Otherwise, the default `TB14` from `global_inputs.py` is used.

2. **Emitter Type Validation**:
   - If the `emitter_type` is not found in the selected `TB14` table, it is automatically set to the first available emitter type, and a warning message is generated.

3. **Generator Flow Temperature Control Type (`gen_flow_temp_control_type`)**:
   - **Type A**: Requires `gen_outdoor_temp_data` as a DataFrame. If not provided, it switches to `Type B` and generates a warning.
   - **Type C**: If `θHW_gen_flw_const` is not provided, it defaults to `50` and a warning is shown.
   - **Invalid Control Type**: Any other values are automatically set to `Type B`.

The function returns:
- The selected `TB14` table.
- The validated `emitter_type`.
- A list of messages about any changes or validations.
- The normalized input configuration.

