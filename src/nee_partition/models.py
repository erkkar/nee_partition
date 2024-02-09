"""Module for respiration and photosynthesis models"""

import numpy as np


def ecosystem_respiration(temperature: float, E: float, R0: float) -> float:
    """Calculate soil respiration based on Lloyd & Taylor (1994)

    Args:
        temperature: Soil temperature (K)
        E: Temperature sensitivity of respiration (K-1)
        R0: Ecosystem respiration at 10°C (mg CO2 m-2 s-1)

    References:
        Lloyd, J., and J. A. Taylor. 1994. ‘On the Temperature Dependence of Soil
        Respiration’. Functional Ecology 8 (3): 315–23.
        https://doi.org/10.2307/2389824.
    """
    temp0 = 56.02  # K
    temp1 = 227.13  # K
    return R0 * np.exp(E * ((1 / temp0) - (1 / (temperature - temp1))))


def gross_primary_productivity(ppfd: float, alpha: float, gp_max: float) -> float:
    """Calculate gross primary productivity based on the hyperbolic light response curve
    (Lasslop et al. 2008)

    Args:
        ppfd: Photosynthetically active radiation (µmol m-2 s-1)
        alpha: Approximation of the canopy light utilization efficiency (µmol-1 m2 s1)
        gp_max: Asymptotic gross photosynthesis rate in optimal light
            conditions (mg CO2 m-2 s-1)

    References:
        Lasslop, G., M. Reichstein, J. Kattge, and D. Papale. 2008. ‘Influences
        of Observation Errors in Eddy Flux Data on Inverse Model Parameter
        Estimation’. Biogeosciences 5 (5): 1311–24.
        https://doi.org/10.5194/bg-5-1311-2008.
    """
    return (alpha * ppfd * gp_max) / (alpha * ppfd + gp_max)
