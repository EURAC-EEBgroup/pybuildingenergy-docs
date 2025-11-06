# ISO 52016 Input Check

The data provided before being used for the simulation are processed and evaluated to be considered fit for the simulation. This process includes a series of checks that allow to identify any potential errors. 
The following controls are applied:

# Thermal and Adjacent Zone
Uno degli errori più caratteristici può essere quello di immetere dei valori errati di superficie della parete di confine tra la zona termica e la zona non termica. Un esempio è quello di dare dei valori più alti della superificie della parete nella zona non termica rispetto alla superificie della parete nella zona termica. In questo caso se il controllo risulta essere negativo allora il tool imposta il valore del superificie della zona non termica uguale a quello della zona termica. 
Qui voglio dire che sebbene la superficie di contatto è la stessa pu`o succedere che la parete della zona termica sia o totlamente a contatto con la zon non termica o solamente una parte a contatto con la zona termica   
