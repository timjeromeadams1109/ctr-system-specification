"""
CTR System - Core Engineering Calculations

This module implements the fundamental structural engineering calculations
for continuous threaded rod design per ASCE 7, NDS, SDPWS, and AISC.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class LoadBasis(Enum):
    ASD = "ASD"
    LRFD = "LRFD"


class RodGrade(Enum):
    ASTM_A307 = "ASTM_A307"
    ASTM_A36 = "ASTM_A36"
    ASTM_A193_B7 = "ASTM_A193_B7"
    ASTM_A449 = "ASTM_A449"


class WoodSpecies(Enum):
    DF_L = "Douglas Fir-Larch"
    SPF = "Spruce-Pine-Fir"
    SYP = "Southern Yellow Pine"
    HEM_FIR = "Hem-Fir"


# Material Properties
MATERIAL_PROPERTIES = {
    RodGrade.ASTM_A307: {"Fy": 36, "Fu": 60},
    RodGrade.ASTM_A36: {"Fy": 36, "Fu": 58},
    RodGrade.ASTM_A193_B7: {"Fy": 105, "Fu": 125},
    RodGrade.ASTM_A449: {"Fy": 92, "Fu": 120}
}

# Thread counts per inch (UNC)
THREAD_COUNT = {
    0.625: 11,
    0.750: 10,
    0.875: 9,
    1.000: 8,
    1.125: 7,
    1.250: 7,
    1.375: 6,
    1.500: 6
}

# Shrinkage coefficients (tangential)
SHRINKAGE_COEFFICIENTS = {
    WoodSpecies.DF_L: 0.00267,
    WoodSpecies.SPF: 0.00236,
    WoodSpecies.SYP: 0.00262,
    WoodSpecies.HEM_FIR: 0.00249
}


def tensile_stress_area(diameter_in: float) -> float:
    """
    Calculate tensile stress area for threaded rod.

    Formula: As = (π/4) × (d - 0.9743/n)²

    Args:
        diameter_in: Nominal rod diameter in inches

    Returns:
        Tensile stress area in square inches
    """
    n = THREAD_COUNT.get(diameter_in, 8)
    As = (math.pi / 4) * (diameter_in - 0.9743 / n) ** 2
    return As


def rod_capacity(
    diameter_in: float,
    grade: RodGrade,
    load_basis: LoadBasis
) -> Tuple[float, float]:
    """
    Calculate rod tension capacity.

    ASD: Ta = (0.75 × Fu × As) / Ω
    LRFD: φTn = φ × 0.75 × Fu × As

    Args:
        diameter_in: Nominal rod diameter
        grade: ASTM grade designation
        load_basis: ASD or LRFD

    Returns:
        Tuple of (allowable_tension_lb, ultimate_tension_lb)
    """
    props = MATERIAL_PROPERTIES.get(grade, MATERIAL_PROPERTIES[RodGrade.ASTM_A307])
    Fu = props["Fu"]  # ksi

    As = tensile_stress_area(diameter_in)

    # Ultimate capacity
    Tu = 0.75 * Fu * As * 1000  # Convert to lbs

    if load_basis == LoadBasis.ASD:
        Omega = 2.0
        Ta = Tu / Omega
    else:  # LRFD
        phi = 0.75
        Ta = phi * Tu

    return (Ta, Tu)


def compute_overturning_moment(
    shear_force_lb: float,
    floor_height_ft: float
) -> float:
    """
    Calculate overturning moment for a shear wall.

    M_OT = V × h

    Args:
        shear_force_lb: Shear force in pounds
        floor_height_ft: Floor-to-floor height in feet

    Returns:
        Overturning moment in ft-lb
    """
    return shear_force_lb * floor_height_ft


def compute_tension_demand(
    overturning_moment_ft_lb: float,
    wall_length_ft: float,
    holdown_offset_in: float,
    tributary_dead_load_lb: float,
    load_basis: LoadBasis
) -> float:
    """
    Compute net tension demand at holdown location.

    T = (M_OT / d) - DL_factor × D

    Args:
        overturning_moment_ft_lb: Overturning moment in ft-lb
        wall_length_ft: Total wall length in feet
        holdown_offset_in: Distance from wall end to holdown (inches)
        tributary_dead_load_lb: Tributary dead load at holdown (lbs)
        load_basis: ASD or LRFD

    Returns:
        Net tension demand in pounds (0 if compression governs)
    """
    # Moment arm (holdown to holdown distance)
    moment_arm_ft = wall_length_ft - (2 * holdown_offset_in / 12)

    if moment_arm_ft <= 0:
        return 0.0

    # Gross uplift from overturning
    gross_uplift = overturning_moment_ft_lb / moment_arm_ft

    # Dead load resistance factor
    dl_factor = 0.6 if load_basis == LoadBasis.ASD else 0.9

    # Resisting dead load
    resisting_dl = dl_factor * tributary_dead_load_lb

    # Net tension (zero if compression)
    net_tension = max(0, gross_uplift - resisting_dl)

    return net_tension


def compute_cumulative_tension(
    level_tensions: Dict[int, float]
) -> Dict[int, float]:
    """
    Compute cumulative tension at each level.

    Rod tension accumulates from top (roof) to bottom (foundation).

    Args:
        level_tensions: Dict mapping level to tension demand

    Returns:
        Dict mapping level to cumulative tension
    """
    sorted_levels = sorted(level_tensions.keys(), reverse=True)

    cumulative = {}
    running_total = 0.0

    for level in sorted_levels:
        running_total += level_tensions[level]
        cumulative[level] = running_total

    return cumulative


def compute_wood_shrinkage(
    thickness_in: float,
    species: WoodSpecies,
    initial_mc: float,
    final_mc: float,
    is_engineered: bool = False
) -> float:
    """
    Calculate wood shrinkage perpendicular to grain.

    Δ = t × S × ΔMC

    Args:
        thickness_in: Thickness perpendicular to grain (inches)
        species: Wood species
        initial_mc: Initial moisture content (percent)
        final_mc: Final moisture content (percent)
        is_engineered: True for EWP (10% of solid sawn shrinkage)

    Returns:
        Shrinkage in inches
    """
    S = SHRINKAGE_COEFFICIENTS.get(species, 0.00250)
    delta_mc = initial_mc - final_mc

    factor = 0.1 if is_engineered else 1.0

    shrinkage = thickness_in * S * delta_mc * factor
    return max(0, shrinkage)


def compute_rod_elongation(
    tension_lb: float,
    length_in: float,
    diameter_in: float,
    E_psi: float = 29_000_000
) -> float:
    """
    Compute rod elongation under tension.

    Δ_rod = (T × L) / (As × E)

    Args:
        tension_lb: Tension force in pounds
        length_in: Rod length in inches
        diameter_in: Rod diameter in inches
        E_psi: Modulus of elasticity (default steel)

    Returns:
        Elongation in inches
    """
    As = tensile_stress_area(diameter_in)
    delta = (tension_lb * length_in) / (As * E_psi)
    return delta


def compute_utilization_ratio(
    demand_lb: float,
    capacity_lb: float
) -> float:
    """
    Compute utilization ratio.

    Args:
        demand_lb: Tension demand
        capacity_lb: Allowable tension capacity

    Returns:
        Utilization ratio (demand/capacity)
    """
    if capacity_lb <= 0:
        return float('inf')
    return demand_lb / capacity_lb


def select_rod_diameter(
    demand_lb: float,
    grade: RodGrade,
    load_basis: LoadBasis,
    max_utilization: float = 0.90,
    min_diameter: float = 0.625,
    max_diameter: float = 1.5
) -> Optional[Dict]:
    """
    Select minimum rod diameter to satisfy demand.

    Args:
        demand_lb: Tension demand in pounds
        grade: Rod material grade
        load_basis: ASD or LRFD
        max_utilization: Maximum acceptable utilization ratio
        min_diameter: Minimum allowable diameter
        max_diameter: Maximum allowable diameter

    Returns:
        Dict with selected diameter and design info, or None if no solution
    """
    available_diameters = [0.625, 0.75, 0.875, 1.0, 1.125, 1.25, 1.375, 1.5]

    for diameter in available_diameters:
        if diameter < min_diameter or diameter > max_diameter:
            continue

        allowable, ultimate = rod_capacity(diameter, grade, load_basis)
        utilization = demand_lb / allowable

        if utilization <= max_utilization:
            return {
                'diameter_in': diameter,
                'tensile_area_sq_in': tensile_stress_area(diameter),
                'allowable_tension_lb': allowable,
                'ultimate_tension_lb': ultimate,
                'demand_lb': demand_lb,
                'utilization_ratio': utilization,
                'status': 'ACCEPTABLE'
            }

    return None


@dataclass
class SeismicParameters:
    """Seismic design parameters per ASCE 7."""
    sds: float
    sd1: float
    R: float = 6.5
    Ie: float = 1.0
    rho: float = 1.0
    omega_0: float = 3.0


def compute_seismic_base_shear(
    params: SeismicParameters,
    seismic_weight_kips: float,
    total_height_ft: float
) -> Dict:
    """
    Compute seismic base shear per ASCE 7-22 §12.8.

    Args:
        params: Seismic design parameters
        seismic_weight_kips: Total seismic weight (kips)
        total_height_ft: Total building height (feet)

    Returns:
        Dict with base shear and related values
    """
    # Approximate period
    T = 0.02 * (total_height_ft ** 0.75)

    # Seismic response coefficient
    Cs = params.sds / (params.R / params.Ie)

    # Upper limit
    if T > 0:
        Cs_max = params.sd1 / (T * params.R / params.Ie)
        Cs = min(Cs, Cs_max)

    # Lower limit
    Cs_min = max(0.044 * params.sds * params.Ie, 0.01)
    Cs = max(Cs, Cs_min)

    # Base shear
    V = Cs * seismic_weight_kips

    return {
        'base_shear_kips': V,
        'Cs': Cs,
        'T_period': T,
        'redundancy_factor': params.rho
    }


def distribute_vertical_forces(
    base_shear_kips: float,
    level_weights: Dict[int, float],
    level_heights: Dict[int, float],
    T_period: float
) -> Dict[int, float]:
    """
    Distribute base shear vertically per ASCE 7-22 §12.8.3.

    Fx = Cvx × V
    Cvx = (wx × hx^k) / Σ(wi × hi^k)

    Args:
        base_shear_kips: Total base shear (kips)
        level_weights: Dict of level -> seismic weight (kips)
        level_heights: Dict of level -> height from base (feet)
        T_period: Building period

    Returns:
        Dict of level -> lateral force (kips)
    """
    # Determine k factor
    if T_period <= 0.5:
        k = 1.0
    elif T_period >= 2.5:
        k = 2.0
    else:
        k = 1.0 + (T_period - 0.5) / 2

    # Compute sum of w*h^k
    sum_wh_k = sum(
        level_weights[level] * (level_heights[level] ** k)
        for level in level_weights
    )

    # Distribute forces
    forces = {}
    for level in level_weights:
        w = level_weights[level]
        h = level_heights[level]
        Cvx = (w * (h ** k)) / sum_wh_k if sum_wh_k > 0 else 0
        Fx = Cvx * base_shear_kips
        forces[level] = Fx

    return forces
