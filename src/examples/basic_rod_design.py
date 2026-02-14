"""
Basic Rod Design Example

Demonstrates core rod sizing calculations for a single rod run
through a 5-story building.
"""

import sys
sys.path.insert(0, '../..')

from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from enum import Enum
import math


class LoadBasis(Enum):
    ASD = "ASD"
    LRFD = "LRFD"


class RodGrade(Enum):
    A307 = "A307"
    A36 = "A36"
    A449 = "A449"
    A193_B7 = "A193-B7"


@dataclass
class RodProperties:
    """Properties for threaded rod materials."""
    grade: RodGrade
    fy_ksi: float  # Yield strength
    fu_ksi: float  # Ultimate strength


ROD_GRADES = {
    RodGrade.A307: RodProperties(RodGrade.A307, 36, 60),
    RodGrade.A36: RodProperties(RodGrade.A36, 36, 58),
    RodGrade.A449: RodProperties(RodGrade.A449, 92, 120),
    RodGrade.A193_B7: RodProperties(RodGrade.A193_B7, 105, 125),
}


# Standard rod diameters (inches)
STANDARD_DIAMETERS = [0.625, 0.750, 0.875, 1.000, 1.125, 1.250, 1.375, 1.500]


@dataclass
class ShearWallInput:
    """Input data for a shear wall at a single level."""
    level: int
    length_ft: float
    unit_shear_plf: int
    story_height_ft: float
    dead_load_plf: float  # Dead load on wall (lb/ft)


@dataclass
class RodDesignResult:
    """Results from rod design calculation."""
    rod_diameter_in: float
    rod_grade: RodGrade
    level_tensions: Dict[int, float]
    cumulative_tensions: Dict[int, float]
    max_tension_lb: float
    allowable_tension_lb: float
    utilization_ratio: float
    total_length_ft: float


def tensile_stress_area(diameter_in: float) -> float:
    """
    Calculate tensile stress area for threaded rod per AISC.

    A_s = (π/4) × (d - 0.9743/n)²

    For UNC threads, n ≈ 8/d for standard sizes.
    """
    # Approximate threads per inch for UNC
    threads_per_inch = {
        0.625: 11,
        0.750: 10,
        0.875: 9,
        1.000: 8,
        1.125: 7,
        1.250: 7,
        1.375: 6,
        1.500: 6,
    }

    n = threads_per_inch.get(diameter_in, 8 / diameter_in)
    d_eff = diameter_in - 0.9743 / n
    return (math.pi / 4) * d_eff ** 2


def compute_overturning_moment(shear_force_lb: float, story_height_ft: float) -> float:
    """
    Calculate overturning moment at base of wall segment.

    M_OT = V × h
    """
    return shear_force_lb * story_height_ft


def compute_tension_demand(
    overturning_moment_ft_lb: float,
    wall_length_ft: float,
    dead_load_lb: float,
    load_basis: LoadBasis = LoadBasis.ASD
) -> float:
    """
    Calculate tension demand at holdown.

    T = (M_OT / d) - C_DL × W_DL

    Where C_DL is the dead load coefficient:
    - ASD: 0.6
    - LRFD: 0.9
    """
    # Moment arm (distance between holdowns)
    # Typically wall length minus 2 × offset (6" each end)
    moment_arm_ft = wall_length_ft - 1.0  # 6" offset each end

    # Dead load coefficient
    c_dl = 0.6 if load_basis == LoadBasis.ASD else 0.9

    # Tension demand
    tension = (overturning_moment_ft_lb / moment_arm_ft) - (c_dl * dead_load_lb)

    return max(0, tension)  # Cannot be negative


def compute_rod_capacity(
    diameter_in: float,
    grade: RodGrade,
    load_basis: LoadBasis = LoadBasis.ASD
) -> float:
    """
    Calculate allowable tension capacity of rod.

    ASD: T_allow = (0.75 × F_u × A_s) / Ω
    LRFD: T_allow = φ × 0.75 × F_u × A_s

    Where Ω = 2.0 (ASD), φ = 0.75 (LRFD)
    """
    props = ROD_GRADES[grade]
    a_s = tensile_stress_area(diameter_in)

    # Nominal strength
    nominal = 0.75 * props.fu_ksi * 1000 * a_s  # Convert ksi to psi

    if load_basis == LoadBasis.ASD:
        return nominal / 2.0  # Ω = 2.0
    else:
        return 0.75 * nominal  # φ = 0.75


def select_rod_diameter(
    required_capacity_lb: float,
    grade: RodGrade = RodGrade.A307,
    load_basis: LoadBasis = LoadBasis.ASD,
    max_utilization: float = 0.95
) -> Optional[Tuple[float, float, float]]:
    """
    Select minimum rod diameter for required capacity.

    Returns: (diameter, capacity, utilization) or None if no size works
    """
    for diameter in STANDARD_DIAMETERS:
        capacity = compute_rod_capacity(diameter, grade, load_basis)
        utilization = required_capacity_lb / capacity

        if utilization <= max_utilization:
            return (diameter, capacity, utilization)

    return None


def design_rod_run(
    walls: List[ShearWallInput],
    load_basis: LoadBasis = LoadBasis.ASD,
    rod_grade: RodGrade = RodGrade.A307
) -> RodDesignResult:
    """
    Design a continuous rod run for a stack of shear walls.

    This calculates tension at each level and selects appropriate rod size.
    """
    # Sort walls by level (top to bottom for accumulation)
    walls_sorted = sorted(walls, key=lambda w: w.level, reverse=True)

    level_tensions = {}
    cumulative_tensions = {}
    cumulative = 0.0
    total_length = 0.0

    for wall in walls_sorted:
        # Calculate shear force at this level
        shear_force = wall.unit_shear_plf * wall.length_ft

        # Calculate overturning moment
        moment = compute_overturning_moment(shear_force, wall.story_height_ft)

        # Calculate dead load resisting
        dead_load = wall.dead_load_plf * wall.length_ft

        # Calculate tension demand at this level
        tension = compute_tension_demand(
            moment,
            wall.length_ft,
            dead_load,
            load_basis
        )

        level_tensions[wall.level] = tension
        cumulative += tension
        cumulative_tensions[wall.level] = cumulative
        total_length += wall.story_height_ft

    # Find maximum cumulative tension
    max_tension = max(cumulative_tensions.values())

    # Select rod size
    selection = select_rod_diameter(max_tension, rod_grade, load_basis)

    if selection is None:
        raise ValueError(f"No standard rod size adequate for {max_tension:.0f} lb demand")

    diameter, capacity, utilization = selection

    return RodDesignResult(
        rod_diameter_in=diameter,
        rod_grade=rod_grade,
        level_tensions=level_tensions,
        cumulative_tensions=cumulative_tensions,
        max_tension_lb=max_tension,
        allowable_tension_lb=capacity,
        utilization_ratio=utilization,
        total_length_ft=total_length
    )


def print_design_results(result: RodDesignResult, rod_run_id: str = "RR-A-01"):
    """Print formatted design results."""
    print("\n" + "=" * 70)
    print(f"ROD RUN DESIGN RESULTS: {rod_run_id}")
    print("=" * 70)

    print(f"\nSelected Rod: {result.rod_diameter_in}\" diameter, {result.rod_grade.value}")
    print(f"Total Length: {result.total_length_ft:.1f} ft")
    print(f"Maximum Tension: {result.max_tension_lb:,.0f} lb")
    print(f"Allowable Tension: {result.allowable_tension_lb:,.0f} lb")
    print(f"Utilization Ratio: {result.utilization_ratio:.2f}")

    print("\n" + "-" * 70)
    print(f"{'Level':<8}{'Level Tension (lb)':<22}{'Cumulative (lb)':<20}{'Status'}")
    print("-" * 70)

    for level in sorted(result.level_tensions.keys(), reverse=True):
        tension = result.level_tensions[level]
        cumulative = result.cumulative_tensions[level]
        utilization = cumulative / result.allowable_tension_lb
        status = "OK" if utilization <= 1.0 else "OVER"

        print(f"{level:<8}{tension:>18,.0f}{cumulative:>20,.0f}    {status}")

    print("-" * 70)
    print()


# Example usage
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("CTR SYSTEM - BASIC ROD DESIGN EXAMPLE")
    print("=" * 70)

    # Define a 5-story shear wall stack
    # Typical Type V wood-frame construction
    wall_stack = [
        ShearWallInput(
            level=5,
            length_ft=12.0,
            unit_shear_plf=350,
            story_height_ft=9.0,
            dead_load_plf=150
        ),
        ShearWallInput(
            level=4,
            length_ft=12.0,
            unit_shear_plf=450,
            story_height_ft=9.5,
            dead_load_plf=180
        ),
        ShearWallInput(
            level=3,
            length_ft=12.0,
            unit_shear_plf=520,
            story_height_ft=9.5,
            dead_load_plf=180
        ),
        ShearWallInput(
            level=2,
            length_ft=12.0,
            unit_shear_plf=580,
            story_height_ft=9.5,
            dead_load_plf=180
        ),
        ShearWallInput(
            level=1,
            length_ft=12.0,
            unit_shear_plf=640,
            story_height_ft=10.0,
            dead_load_plf=200
        ),
    ]

    print("\nInput Shear Wall Stack:")
    print("-" * 70)
    print(f"{'Level':<8}{'Length (ft)':<14}{'Unit Shear (plf)':<18}{'Height (ft)'}")
    print("-" * 70)
    for wall in wall_stack:
        print(f"{wall.level:<8}{wall.length_ft:<14.1f}{wall.unit_shear_plf:<18}{wall.story_height_ft:.1f}")

    # Design with ASD
    print("\n\n>>> Designing with ASD load basis...")
    result_asd = design_rod_run(wall_stack, LoadBasis.ASD, RodGrade.A307)
    print_design_results(result_asd, "RR-A-01")

    # Design with LRFD
    print("\n>>> Designing with LRFD load basis...")
    result_lrfd = design_rod_run(wall_stack, LoadBasis.LRFD, RodGrade.A307)
    print_design_results(result_lrfd, "RR-A-01-LRFD")

    # Try with higher grade material
    print("\n>>> Designing with A449 high-strength rod...")
    result_high = design_rod_run(wall_stack, LoadBasis.ASD, RodGrade.A449)
    print_design_results(result_high, "RR-A-01-HS")

    # Summary comparison
    print("\n" + "=" * 70)
    print("DESIGN COMPARISON SUMMARY")
    print("=" * 70)
    print(f"{'Method':<20}{'Diameter':<12}{'Grade':<12}{'Utilization'}")
    print("-" * 70)
    print(f"{'ASD':<20}{result_asd.rod_diameter_in}\"{'':8}{result_asd.rod_grade.value:<12}{result_asd.utilization_ratio:.2f}")
    print(f"{'LRFD':<20}{result_lrfd.rod_diameter_in}\"{'':8}{result_lrfd.rod_grade.value:<12}{result_lrfd.utilization_ratio:.2f}")
    print(f"{'ASD + A449':<20}{result_high.rod_diameter_in}\"{'':8}{result_high.rod_grade.value:<12}{result_high.utilization_ratio:.2f}")
    print()
