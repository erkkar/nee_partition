NEE_partitioning
================

A Python package for partitioning measured Net Ecosystem Exchange (NEE) of CO₂
into Total Ecosystem Respiration (TER) and Gross Primary Productivity (GPP).

Installation and usage
----------------------

To install the package from GitHub

    $ pip install git+https://github.com/erkkar/nee_partition

Basic usage

    >>>> from nee_partition.main import main
    >>>> main()

Methodology
-----------

Ecosystem respiration as a function of temperature is modelled 
following Lloyd and Taylor (1994):
```math
R_\mathrm{eco}(T) 
    = R_0 \exp\left[E\left(\frac{1}{T_0} - \frac{1}{T - T_1}\right)\right],
```
where $R_0$ is the ecosystem respiration at the reference temperature (10°C),
$E$ is the temperature sensitivity of respiration and $T_0, T_1$ are 
temperature constants.

GPP is modelled using a hyperbolic light response curve (Lasslop et al., 2008):
```math
\mathit{GPP} 
    = \frac{\alpha \times \mathit{PPFD} \times \mathit{GP}_\mathrm{max}}
           {\alpha \times \mathit{PPFD} + \mathit{GP}_\mathrm{max}},
```
where $\alpha$ is the canopy light utilization efficiency 
and $\mathit{GP}_\mathrm{max}$ the asymptotic gross photosynthesis rate.

References
----------
Lasslop, G., M. Reichstein, J. Kattge, and D. Papale. 2008. ‘Influences
of Observation Errors in Eddy Flux Data on Inverse Model Parameter
Estimation’. Biogeosciences 5 (5): 1311–24.
https://doi.org/10.5194/bg-5-1311-2008.

Lloyd, J., and J. A. Taylor. 1994. ‘On the Temperature Dependence of Soil
Respiration’. Functional Ecology 8 (3): 315–23.
https://doi.org/10.2307/2389824.
