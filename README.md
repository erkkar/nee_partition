NEE_partitioning
================

A Python package for partitioning measured Net Ecosystem Exchange (NEE) of CO₂
into Total Ecosystem Respiration (TER) and Gross Primary Productivity (GPP).

Installation and usage
----------------------

To install the package from GitHub

    $ pip install git+https://github.com/erkkar/nee_partition

Basic usage

    >>> from nee_partition.main import main
    >>> main("<PATH TO A CSV DATA FILE>")

Methodology
-----------

The partitioning  uses a modified version of the algorithm described by 
Reichstein et al. (2005).

Ecosystem respiration as a function of temperature is modelled 
following Lloyd and Taylor (1994, Eq. 11):
```math
R_\mathrm{eco}(T) 
    = R_{10} 
        \exp\left[
            E_0 \left(\frac{1}{T_\mathrm{ref} - T_0} - \frac{1}{T - T_0}\right)
        \right],
```
where $R_{10}$ is the ecosystem respiration at the reference temperature 
$T_\mathrm{ref}$ (10°), $E_0$ the temperature sensitivity of respiration 
and the constant $T_0$ has value 227.13 K.

Parameter $E_0$ is estimated by fitting the model to night-time data in 
15-day windows around each day, and taking the median of the fitted values.
Then, parameter $R_{10}$ is found for each day by fitting the model with 
constant $E_0$ using 5 to 15-day windows of night-time data 
so that there is enough data points and the fit fulfils quality criteria.

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
Estimation’. *Biogeosciences* 5 (5): 1311–24.
https://doi.org/10.5194/bg-5-1311-2008.

Lloyd, J., and J. A. Taylor. 1994. ‘On the Temperature Dependence of Soil
Respiration’. *Functional Ecology* 8 (3): 315–23.
https://doi.org/10.2307/2389824.

Reichstein, Markus, Eva Falge, Dennis Baldocchi, Dario Papale, Marc Aubinet, Paul Berbigier, Christian Bernhofer, et al. 2005. ‘On the Separation of Net Ecosystem Exchange into Assimilation and Ecosystem Respiration: Review and Improved Algorithm’. *Global Change Biology* 11 (9): 1424–39. https://doi.org/10.1111/j.1365-2486.2005.001002.x.

