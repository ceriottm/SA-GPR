#!/bin/bash
f2py=f2py
cd utils
 $f2py -c --opt='-O3' fill_power_spectra.f90 -m pow_spec
 $f2py -c --opt='-O3' combine_spectra.f90 -m com_spe
cd ../
