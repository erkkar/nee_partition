"""Module for gross primary productivity modelling"""

VARIABLE_BOUNDS = {
    "alpha": (-0.02, -0.0000001),  # µmol-1 m2 s1
    "gp_max": (-5, -0.00000001),  # mg CO2 m-2 s-1
}


def gpp_light_response(ppfd: float, alpha: float, gp_max: float) -> float:
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
