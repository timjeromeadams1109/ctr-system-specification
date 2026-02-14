"""
Shrinkage Analysis Example

Demonstrates wood shrinkage and rod elongation calculations
for take-up device specification.
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple
from enum import Enum
import math


class WoodSpecies(Enum):
    DOUGLAS_FIR_LARCH = "Douglas Fir-Larch"
    SOUTHERN_PINE = "Southern Pine"
    SPRUCE_PINE_FIR = "Spruce-Pine-Fir"
    HEM_FIR = "Hem-Fir"


class GrainDirection(Enum):
    PERPENDICULAR = "perpendicular"  # Tangential/radial shrinkage
    PARALLEL = "parallel"  # Longitudinal (negligible)


@dataclass
class WoodShrinkageProperties:
    """Shrinkage coefficients by species."""
    species: WoodSpecies
    tangential_coeff: float  # % per 1% MC change
    radial_coeff: float


SHRINKAGE_COEFFICIENTS = {
    WoodSpecies.DOUGLAS_FIR_LARCH: WoodShrinkageProperties(
        WoodSpecies.DOUGLAS_FIR_LARCH, 0.00267, 0.00179
    ),
    WoodSpecies.SOUTHERN_PINE: WoodShrinkageProperties(
        WoodSpecies.SOUTHERN_PINE, 0.00263, 0.00178
    ),
    WoodSpecies.SPRUCE_PINE_FIR: WoodShrinkageProperties(
        WoodSpecies.SPRUCE_PINE_FIR, 0.00258, 0.00149
    ),
    WoodSpecies.HEM_FIR: WoodShrinkageProperties(
        WoodSpecies.HEM_FIR, 0.00268, 0.00159
    ),
}


@dataclass
class FloorAssembly:
    """Definition of a floor assembly for shrinkage calculation."""
    level: int
    top_plate_depth_in: float  # Typically 1.5" (single) or 3.0" (double)
    bottom_plate_depth_in: float  # Typically 1.5"
    joist_depth_in: float  # Floor joist depth
    rim_depth_in: float  # Rim board depth (if different from joist)
    species: WoodSpecies


@dataclass
class TakeUpDevice:
    """Take-up device specifications."""
    model: str
    manufacturer: str
    travel_capacity_in: float
    allowable_load_lb: float


# Common take-up devices
TAKE_UP_DEVICES = [
    TakeUpDevice("RTUD3", "Simpson", 0.75, 16000),
    TakeUpDevice("RTUD4", "Simpson", 1.00, 24500),
    TakeUpDevice("RTUD5", "Simpson", 1.25, 32500),
    TakeUpDevice("RTUD6", "Simpson", 1.50, 40500),
    TakeUpDevice("RTUD7", "Simpson", 2.00, 48000),
    TakeUpDevice("ATUD9", "Simpson", 2.25, 14705),
    TakeUpDevice("ATUD14", "Simpson", 3.00, 23110),
]


def compute_wood_shrinkage(
    thickness_in: float,
    species: WoodSpecies,
    initial_mc: float = 19.0,
    final_mc: float = 12.0,
    grain_direction: GrainDirection = GrainDirection.PERPENDICULAR
) -> float:
    """
    Calculate wood shrinkage perpendicular to grain.

    Δ_shrinkage = t × S × ΔMC

    Where:
    - t = thickness perpendicular to grain
    - S = shrinkage coefficient
    - ΔMC = change in moisture content

    Per NDS, shrinkage only occurs below fiber saturation point (~30% MC).
    For S-Green lumber, initial MC is typically 19%.
    """
    props = SHRINKAGE_COEFFICIENTS[species]

    if grain_direction == GrainDirection.PARALLEL:
        return 0.0  # Longitudinal shrinkage is negligible

    # Use average of tangential and radial (conservative)
    avg_coeff = (props.tangential_coeff + props.radial_coeff) / 2

    # Calculate MC change (only below fiber saturation point)
    effective_initial = min(initial_mc, 30.0)
    effective_final = min(final_mc, 30.0)
    delta_mc = effective_initial - effective_final

    # Calculate shrinkage
    shrinkage = thickness_in * avg_coeff * delta_mc

    return max(0, shrinkage)


def compute_rod_elongation(
    tension_lb: float,
    length_in: float,
    diameter_in: float,
    elastic_modulus_psi: float = 29_000_000
) -> float:
    """
    Calculate rod elongation under tension.

    Δ_rod = (T × L) / (A_s × E)

    Where:
    - T = tension force
    - L = rod length
    - A_s = tensile stress area
    - E = elastic modulus
    """
    # Calculate tensile stress area
    threads_per_inch = {
        0.625: 11, 0.750: 10, 0.875: 9, 1.000: 8,
        1.125: 7, 1.250: 7, 1.375: 6, 1.500: 6,
    }
    n = threads_per_inch.get(diameter_in, 8 / diameter_in)
    d_eff = diameter_in - 0.9743 / n
    a_s = (math.pi / 4) * d_eff ** 2

    # Calculate elongation
    elongation = (tension_lb * length_in) / (a_s * elastic_modulus_psi)

    return elongation


def analyze_floor_shrinkage(assembly: FloorAssembly) -> Dict[str, float]:
    """
    Calculate shrinkage for a single floor assembly.

    Components that shrink:
    - Top plates (perpendicular to grain)
    - Bottom plates (perpendicular to grain)
    - Floor joists/rim (perpendicular to grain at bearing)
    """
    species = assembly.species

    # Top plate shrinkage
    top_plate_shrink = compute_wood_shrinkage(
        assembly.top_plate_depth_in,
        species
    )

    # Bottom plate shrinkage
    bottom_plate_shrink = compute_wood_shrinkage(
        assembly.bottom_plate_depth_in,
        species
    )

    # Joist/rim shrinkage (at bearing point)
    joist_shrink = compute_wood_shrinkage(
        assembly.joist_depth_in,
        species
    )

    total = top_plate_shrink + bottom_plate_shrink + joist_shrink

    return {
        'level': assembly.level,
        'top_plate_in': top_plate_shrink,
        'bottom_plate_in': bottom_plate_shrink,
        'joist_in': joist_shrink,
        'total_in': total
    }


@dataclass
class ShrinkageAnalysisResult:
    """Complete shrinkage analysis results."""
    floor_details: List[Dict[str, float]]
    total_shrinkage_in: float
    rod_elongation_in: float
    net_movement_in: float
    required_travel_in: float
    recommended_device: TakeUpDevice
    placement_level: int


def analyze_rod_run_shrinkage(
    floor_assemblies: List[FloorAssembly],
    rod_diameter_in: float,
    rod_length_ft: float,
    max_tension_lb: float,
    safety_factor: float = 1.25
) -> ShrinkageAnalysisResult:
    """
    Complete shrinkage analysis for a rod run.

    Calculates:
    1. Total wood shrinkage through all floors
    2. Rod elongation under maximum tension
    3. Net movement (shrinkage - elongation)
    4. Required take-up device travel
    5. Recommended device and placement
    """
    # Analyze each floor
    floor_details = [analyze_floor_shrinkage(assembly) for assembly in floor_assemblies]

    # Sum total shrinkage
    total_shrinkage = sum(fd['total_in'] for fd in floor_details)

    # Calculate rod elongation
    rod_length_in = rod_length_ft * 12
    rod_elongation = compute_rod_elongation(
        max_tension_lb,
        rod_length_in,
        rod_diameter_in
    )

    # Net movement (positive = compression, needs take-up)
    net_movement = total_shrinkage - rod_elongation

    # Required travel with safety factor
    required_travel = max(0, net_movement * safety_factor)

    # Select take-up device
    recommended_device = None
    for device in TAKE_UP_DEVICES:
        if device.travel_capacity_in >= required_travel:
            if device.allowable_load_lb >= max_tension_lb:
                recommended_device = device
                break

    if recommended_device is None:
        # Fall back to largest device
        recommended_device = TAKE_UP_DEVICES[-1]

    # Determine placement level (typically at mid-height or Level 3)
    num_floors = len(floor_assemblies)
    placement_level = min(3, (num_floors + 1) // 2 + 1)

    return ShrinkageAnalysisResult(
        floor_details=floor_details,
        total_shrinkage_in=total_shrinkage,
        rod_elongation_in=rod_elongation,
        net_movement_in=net_movement,
        required_travel_in=required_travel,
        recommended_device=recommended_device,
        placement_level=placement_level
    )


def print_shrinkage_analysis(result: ShrinkageAnalysisResult, rod_run_id: str = "RR-A-01"):
    """Print formatted shrinkage analysis results."""
    print("\n" + "=" * 70)
    print(f"SHRINKAGE ANALYSIS RESULTS: {rod_run_id}")
    print("=" * 70)

    print("\nFloor-by-Floor Shrinkage:")
    print("-" * 70)
    print(f"{'Level':<8}{'Top Plate':<14}{'Bottom Plate':<14}{'Joist':<12}{'Total'}")
    print("-" * 70)

    for fd in sorted(result.floor_details, key=lambda x: x['level'], reverse=True):
        print(f"{int(fd['level']):<8}{fd['top_plate_in']:>10.4f}\"{fd['bottom_plate_in']:>12.4f}\"{fd['joist_in']:>10.4f}\"{fd['total_in']:>10.4f}\"")

    print("-" * 70)
    print(f"{'TOTAL':<8}{'':<14}{'':<14}{'':<12}{result.total_shrinkage_in:>10.4f}\"")

    print("\n" + "-" * 70)
    print("Movement Summary:")
    print("-" * 70)
    print(f"Total Wood Shrinkage:     {result.total_shrinkage_in:>8.4f}\"")
    print(f"Rod Elongation:           {result.rod_elongation_in:>8.4f}\"")
    print(f"Net Movement:             {result.net_movement_in:>8.4f}\"")
    print(f"Required Travel (×1.25):  {result.required_travel_in:>8.4f}\"")

    print("\n" + "-" * 70)
    print("Take-Up Device Recommendation:")
    print("-" * 70)
    dev = result.recommended_device
    print(f"Model:            {dev.model}")
    print(f"Manufacturer:     {dev.manufacturer}")
    print(f"Travel Capacity:  {dev.travel_capacity_in:.2f}\"")
    print(f"Allowable Load:   {dev.allowable_load_lb:,} lb")
    print(f"Placement:        Level {result.placement_level}")

    margin = dev.travel_capacity_in - result.required_travel_in
    print(f"Travel Margin:    {margin:.3f}\" ({margin/dev.travel_capacity_in*100:.1f}%)")
    print()


# Example usage
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("CTR SYSTEM - SHRINKAGE ANALYSIS EXAMPLE")
    print("=" * 70)

    # Define 5-story floor assemblies
    # Typical Type V wood-frame construction
    floor_assemblies = [
        FloorAssembly(
            level=5,
            top_plate_depth_in=3.0,    # Double top plate
            bottom_plate_depth_in=1.5,  # Single bottom plate
            joist_depth_in=11.875,      # TJI 11-7/8" I-joist
            rim_depth_in=11.875,
            species=WoodSpecies.DOUGLAS_FIR_LARCH
        ),
        FloorAssembly(
            level=4,
            top_plate_depth_in=3.0,
            bottom_plate_depth_in=1.5,
            joist_depth_in=11.875,
            rim_depth_in=11.875,
            species=WoodSpecies.DOUGLAS_FIR_LARCH
        ),
        FloorAssembly(
            level=3,
            top_plate_depth_in=3.0,
            bottom_plate_depth_in=1.5,
            joist_depth_in=11.875,
            rim_depth_in=11.875,
            species=WoodSpecies.DOUGLAS_FIR_LARCH
        ),
        FloorAssembly(
            level=2,
            top_plate_depth_in=3.0,
            bottom_plate_depth_in=1.5,
            joist_depth_in=14.0,        # 14" TJI for longer spans
            rim_depth_in=14.0,
            species=WoodSpecies.DOUGLAS_FIR_LARCH
        ),
        FloorAssembly(
            level=1,
            top_plate_depth_in=3.0,
            bottom_plate_depth_in=1.5,
            joist_depth_in=0.0,         # Slab on grade (no joist shrinkage)
            rim_depth_in=0.0,
            species=WoodSpecies.DOUGLAS_FIR_LARCH
        ),
    ]

    print("\nInput Floor Assemblies:")
    print("-" * 70)
    print(f"{'Level':<8}{'Top Plate':<12}{'Bot Plate':<12}{'Joist':<12}{'Species'}")
    print("-" * 70)
    for assembly in floor_assemblies:
        print(f"{assembly.level:<8}{assembly.top_plate_depth_in:<12.2f}{assembly.bottom_plate_depth_in:<12.2f}{assembly.joist_depth_in:<12.2f}{assembly.species.value}")

    # Rod parameters
    rod_diameter = 0.875  # inches
    rod_length = 47.5  # feet (5 stories)
    max_tension = 28450  # lb (from previous example)

    print(f"\nRod Parameters:")
    print(f"  Diameter: {rod_diameter}\"")
    print(f"  Length: {rod_length} ft")
    print(f"  Max Tension: {max_tension:,} lb")

    # Perform analysis
    result = analyze_rod_run_shrinkage(
        floor_assemblies,
        rod_diameter,
        rod_length,
        max_tension
    )

    print_shrinkage_analysis(result, "RR-A-01")

    # Show comparison with different joist depths
    print("\n" + "=" * 70)
    print("SENSITIVITY ANALYSIS: Effect of Joist Depth")
    print("=" * 70)

    joist_depths = [9.5, 11.875, 14.0, 16.0]
    print(f"\n{'Joist Depth':<14}{'Total Shrink':<16}{'Net Movement':<16}{'Required Device'}")
    print("-" * 70)

    for depth in joist_depths:
        test_assemblies = [
            FloorAssembly(
                level=i,
                top_plate_depth_in=3.0,
                bottom_plate_depth_in=1.5,
                joist_depth_in=depth if i > 1 else 0,
                rim_depth_in=depth if i > 1 else 0,
                species=WoodSpecies.DOUGLAS_FIR_LARCH
            )
            for i in range(5, 0, -1)
        ]

        test_result = analyze_rod_run_shrinkage(
            test_assemblies,
            rod_diameter,
            rod_length,
            max_tension
        )

        print(f"{depth}\"{'':10}{test_result.total_shrinkage_in:.4f}\"{'':10}{test_result.net_movement_in:.4f}\"{'':10}{test_result.recommended_device.model}")

    print()
