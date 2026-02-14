"""
Clash Detection Example

Demonstrates 3D spatial indexing and geometric intersection
detection between rod runs and MEP elements.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Generator
from enum import Enum
import math


class ElementType(Enum):
    ROD = "ROD"
    HVAC_DUCT = "HVAC_DUCT"
    PLUMBING_PIPE = "PLUMBING_PIPE"
    ELECTRICAL_CONDUIT = "ELECTRICAL_CONDUIT"
    FIRE_SPRINKLER = "FIRE_SPRINKLER"
    STRUCTURAL_BEAM = "STRUCTURAL_BEAM"
    CABLE_TRAY = "CABLE_TRAY"


class ClashSeverity(Enum):
    CRITICAL = "CRITICAL"  # Hard interference
    MAJOR = "MAJOR"        # Clearance violation > 50%
    MINOR = "MINOR"        # Clearance violation < 50%
    WARNING = "WARNING"    # Near limit


# Minimum clearances by element type (inches)
CLEARANCE_REQUIREMENTS = {
    ElementType.HVAC_DUCT: 2.0,
    ElementType.PLUMBING_PIPE: 1.5,
    ElementType.ELECTRICAL_CONDUIT: 1.0,
    ElementType.FIRE_SPRINKLER: 2.0,
    ElementType.STRUCTURAL_BEAM: 0.5,
    ElementType.CABLE_TRAY: 1.5,
}


@dataclass
class Point3D:
    """3D point representation."""
    x: float
    y: float
    z: float

    def __add__(self, other: 'Point3D') -> 'Point3D':
        return Point3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: 'Point3D') -> 'Point3D':
        return Point3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> 'Point3D':
        return Point3D(self.x * scalar, self.y * scalar, self.z * scalar)

    def dot(self, other: 'Point3D') -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def length(self) -> float:
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalized(self) -> 'Point3D':
        length = self.length()
        if length == 0:
            return Point3D(0, 0, 0)
        return Point3D(self.x / length, self.y / length, self.z / length)


@dataclass
class BoundingBox:
    """Axis-aligned bounding box."""
    min_point: Point3D
    max_point: Point3D

    def intersects(self, other: 'BoundingBox') -> bool:
        """Check if two bounding boxes intersect."""
        return (
            self.min_point.x <= other.max_point.x and
            self.max_point.x >= other.min_point.x and
            self.min_point.y <= other.max_point.y and
            self.max_point.y >= other.min_point.y and
            self.min_point.z <= other.max_point.z and
            self.max_point.z >= other.min_point.z
        )

    def expand(self, amount: float) -> 'BoundingBox':
        """Return expanded bounding box."""
        return BoundingBox(
            Point3D(
                self.min_point.x - amount,
                self.min_point.y - amount,
                self.min_point.z - amount
            ),
            Point3D(
                self.max_point.x + amount,
                self.max_point.y + amount,
                self.max_point.z + amount
            )
        )

    def to_tuple(self) -> Tuple[float, ...]:
        """Convert to tuple for R-tree indexing."""
        return (
            self.min_point.x, self.min_point.y, self.min_point.z,
            self.max_point.x, self.max_point.y, self.max_point.z
        )


@dataclass
class Cylinder:
    """Cylinder representation for rods and pipes."""
    start: Point3D
    end: Point3D
    radius: float

    def get_bounds(self) -> BoundingBox:
        """Calculate axis-aligned bounding box."""
        return BoundingBox(
            Point3D(
                min(self.start.x, self.end.x) - self.radius,
                min(self.start.y, self.end.y) - self.radius,
                min(self.start.z, self.end.z) - self.radius
            ),
            Point3D(
                max(self.start.x, self.end.x) + self.radius,
                max(self.start.y, self.end.y) + self.radius,
                max(self.start.z, self.end.z) + self.radius
            )
        )


@dataclass
class Box:
    """Box representation for ducts and beams."""
    center: Point3D
    width: float   # X dimension
    height: float  # Y dimension
    depth: float   # Z dimension

    def get_bounds(self) -> BoundingBox:
        """Calculate axis-aligned bounding box."""
        half_w = self.width / 2
        half_h = self.height / 2
        half_d = self.depth / 2
        return BoundingBox(
            Point3D(
                self.center.x - half_w,
                self.center.y - half_h,
                self.center.z - half_d
            ),
            Point3D(
                self.center.x + half_w,
                self.center.y + half_h,
                self.center.z + half_d
            )
        )


@dataclass
class SpatialElement:
    """Element with spatial representation."""
    element_id: str
    element_type: ElementType
    geometry: object  # Cylinder or Box
    level: int
    description: str = ""

    def get_bounds(self) -> BoundingBox:
        return self.geometry.get_bounds()


@dataclass
class ClashResult:
    """Result of clash detection between two elements."""
    element_1_id: str
    element_2_id: str
    element_1_type: ElementType
    element_2_type: ElementType
    severity: ClashSeverity
    penetration_in: float
    clearance_required_in: float
    clearance_actual_in: float
    intersection_point: Point3D
    level: int
    description: str
    recommendations: List[str] = field(default_factory=list)


def distance_point_to_line_segment(
    point: Point3D,
    line_start: Point3D,
    line_end: Point3D
) -> Tuple[float, float]:
    """
    Calculate distance from point to line segment.

    Returns: (distance, parameter t along line)
    """
    v = line_end - line_start
    w = point - line_start

    c1 = w.dot(v)
    c2 = v.dot(v)

    if c2 == 0:
        # Degenerate segment (point)
        return (point - line_start).length(), 0.0

    t = c1 / c2

    if t <= 0:
        return (point - line_start).length(), 0.0
    elif t >= 1:
        return (point - line_end).length(), 1.0
    else:
        closest = line_start + v * t
        return (point - closest).length(), t


def cylinder_cylinder_intersection(
    cyl1: Cylinder,
    cyl2: Cylinder
) -> Tuple[bool, Optional[float], Optional[Point3D]]:
    """
    Detect intersection between two finite cylinders.

    Returns: (intersects, penetration_depth, intersection_point)
    """
    # Direction vectors
    d1 = cyl1.end - cyl1.start
    d2 = cyl2.end - cyl2.start

    len1 = d1.length()
    len2 = d2.length()

    if len1 == 0 or len2 == 0:
        return (False, None, None)

    # Unit direction vectors
    u1 = d1.normalized()
    u2 = d2.normalized()

    # Find closest points between axis lines
    w = cyl1.start - cyl2.start
    a = u1.dot(u1)  # = 1
    b = u1.dot(u2)
    c = u2.dot(u2)  # = 1
    d = u1.dot(w)
    e = u2.dot(w)

    denom = a * c - b * b

    if abs(denom) < 1e-10:
        # Lines are parallel
        t1, t2 = 0, -e / c if c != 0 else 0
    else:
        t1 = (b * e - c * d) / denom
        t2 = (a * e - b * d) / denom

    # Clamp to segment bounds
    t1 = max(0, min(1, t1 / len1)) * len1 if len1 > 0 else 0
    t2 = max(0, min(1, t2 / len2)) * len2 if len2 > 0 else 0

    # Closest points on each axis
    closest1 = cyl1.start + d1.normalized() * t1 if len1 > 0 else cyl1.start
    closest2 = cyl2.start + d2.normalized() * t2 if len2 > 0 else cyl2.start

    # Distance between closest points
    distance = (closest1 - closest2).length()
    combined_radius = cyl1.radius + cyl2.radius

    if distance < combined_radius:
        penetration = combined_radius - distance
        intersection_point = closest1 + (closest2 - closest1) * 0.5
        return (True, penetration, intersection_point)

    return (False, None, None)


def cylinder_box_intersection(
    cyl: Cylinder,
    box: Box
) -> Tuple[bool, Optional[float], Optional[Point3D]]:
    """
    Detect intersection between cylinder and axis-aligned box.
    Uses sampling along cylinder axis.
    """
    d = cyl.end - cyl.start
    length = d.length()

    bounds = box.get_bounds()

    if length == 0:
        # Point cylinder
        closest = Point3D(
            max(bounds.min_point.x, min(cyl.start.x, bounds.max_point.x)),
            max(bounds.min_point.y, min(cyl.start.y, bounds.max_point.y)),
            max(bounds.min_point.z, min(cyl.start.z, bounds.max_point.z))
        )
        dist = (cyl.start - closest).length()
        if dist < cyl.radius:
            return (True, cyl.radius - dist, cyl.start)
        return (False, None, None)

    # Sample points along cylinder axis
    num_samples = max(10, int(length / cyl.radius))
    min_clearance = float('inf')
    min_point = None

    for i in range(num_samples + 1):
        t = i / num_samples
        point = cyl.start + d * t

        # Find closest point on box surface
        closest = Point3D(
            max(bounds.min_point.x, min(point.x, bounds.max_point.x)),
            max(bounds.min_point.y, min(point.y, bounds.max_point.y)),
            max(bounds.min_point.z, min(point.z, bounds.max_point.z))
        )

        dist = (point - closest).length()

        if dist < min_clearance:
            min_clearance = dist
            min_point = closest

        if dist < cyl.radius:
            penetration = cyl.radius - dist
            return (True, penetration, closest)

    # No intersection but return closest approach
    return (False, cyl.radius - min_clearance, min_point)


class SpatialIndex:
    """Simple spatial index for clash detection (without rtree dependency)."""

    def __init__(self):
        self.elements: Dict[str, SpatialElement] = {}

    def insert(self, element: SpatialElement):
        """Insert element into index."""
        self.elements[element.element_id] = element

    def query_potential_clashes(
        self,
        bounds: BoundingBox,
        exclude_id: str = None
    ) -> Generator[SpatialElement, None, None]:
        """Find elements that might clash with given bounds."""
        for elem_id, element in self.elements.items():
            if elem_id == exclude_id:
                continue
            if bounds.intersects(element.get_bounds()):
                yield element


class ClashDetectionEngine:
    """Engine for detecting clashes between building elements."""

    def __init__(self, clearance_multiplier: float = 1.0):
        self.index = SpatialIndex()
        self.clearance_multiplier = clearance_multiplier

    def add_element(self, element: SpatialElement):
        """Add element to the spatial index."""
        self.index.insert(element)

    def get_required_clearance(self, element_type: ElementType) -> float:
        """Get required clearance for element type."""
        base = CLEARANCE_REQUIREMENTS.get(element_type, 1.0)
        return base * self.clearance_multiplier

    def classify_severity(
        self,
        penetration: float,
        element_type: ElementType
    ) -> Tuple[ClashSeverity, str]:
        """Classify clash severity and generate description."""
        required = self.get_required_clearance(element_type)

        if penetration > 0:
            return (
                ClashSeverity.CRITICAL,
                f"Hard interference: {penetration:.2f}\" overlap"
            )

        actual_clearance = -penetration

        if actual_clearance < required:
            violation = required - actual_clearance
            if violation > required * 0.5:
                return (
                    ClashSeverity.MAJOR,
                    f"Clearance violation: {actual_clearance:.2f}\" vs {required:.2f}\" required"
                )
            else:
                return (
                    ClashSeverity.MINOR,
                    f"Minor clearance violation: {actual_clearance:.2f}\" vs {required:.2f}\" required"
                )

        if actual_clearance < required * 1.5:
            return (
                ClashSeverity.WARNING,
                f"Near clearance limit: {actual_clearance:.2f}\" (min {required:.2f}\")"
            )

        return (None, "")  # No clash

    def generate_recommendations(
        self,
        severity: ClashSeverity,
        element_type: ElementType
    ) -> List[str]:
        """Generate resolution recommendations."""
        recommendations = []

        trade_map = {
            ElementType.HVAC_DUCT: "MECHANICAL",
            ElementType.PLUMBING_PIPE: "PLUMBING",
            ElementType.ELECTRICAL_CONDUIT: "ELECTRICAL",
            ElementType.FIRE_SPRINKLER: "FIRE_PROTECTION",
            ElementType.STRUCTURAL_BEAM: "STRUCTURAL",
            ElementType.CABLE_TRAY: "ELECTRICAL",
        }

        trade = trade_map.get(element_type, "COORDINATION")

        if severity == ClashSeverity.CRITICAL:
            recommendations.append(
                f"RELOCATE_MEP: Move {element_type.value} to clear rod path "
                f"(Responsible: {trade})"
            )
            recommendations.append(
                "RELOCATE_ROD: Move rod run if MEP is fixed "
                "(Requires structural review)"
            )
        elif severity == ClashSeverity.MAJOR:
            recommendations.append(
                f"ADJUST_ROUTING: Modify {element_type.value} routing "
                f"(Responsible: {trade})"
            )
        elif severity == ClashSeverity.MINOR:
            recommendations.append(
                "VERIFY_FIELD: Confirm clearance acceptable in field"
            )

        return recommendations

    def check_clash(
        self,
        rod: SpatialElement,
        other: SpatialElement
    ) -> Optional[ClashResult]:
        """Check for clash between rod and another element."""
        rod_geom = rod.geometry
        other_geom = other.geometry

        # Determine intersection based on geometry types
        if isinstance(other_geom, Cylinder):
            intersects, penetration, point = cylinder_cylinder_intersection(
                rod_geom, other_geom
            )
        elif isinstance(other_geom, Box):
            intersects, penetration, point = cylinder_box_intersection(
                rod_geom, other_geom
            )
        else:
            return None

        if penetration is None:
            return None

        # Classify severity
        severity, description = self.classify_severity(
            penetration, other.element_type
        )

        if severity is None:
            return None

        required_clearance = self.get_required_clearance(other.element_type)
        actual_clearance = -penetration if penetration < 0 else 0

        recommendations = self.generate_recommendations(
            severity, other.element_type
        )

        return ClashResult(
            element_1_id=rod.element_id,
            element_2_id=other.element_id,
            element_1_type=rod.element_type,
            element_2_type=other.element_type,
            severity=severity,
            penetration_in=max(0, penetration),
            clearance_required_in=required_clearance,
            clearance_actual_in=actual_clearance,
            intersection_point=point if point else Point3D(0, 0, 0),
            level=rod.level,
            description=description,
            recommendations=recommendations
        )

    def detect_all_clashes(self, clearance_buffer: float = 2.0) -> List[ClashResult]:
        """Detect all clashes involving rod elements."""
        clashes = []

        rods = [
            elem for elem in self.index.elements.values()
            if elem.element_type == ElementType.ROD
        ]

        for rod in rods:
            # Expand bounds for clearance check
            search_bounds = rod.get_bounds().expand(clearance_buffer)

            for other in self.index.query_potential_clashes(
                search_bounds, exclude_id=rod.element_id
            ):
                if other.element_type == ElementType.ROD:
                    continue  # Skip rod-to-rod

                clash = self.check_clash(rod, other)
                if clash:
                    clashes.append(clash)

        return clashes


def print_clash_report(clashes: List[ClashResult]):
    """Print formatted clash detection report."""
    print("\n" + "=" * 70)
    print("CLASH DETECTION REPORT")
    print("=" * 70)

    if not clashes:
        print("\nNo clashes detected.")
        return

    # Group by severity
    by_severity = {s: [] for s in ClashSeverity}
    for clash in clashes:
        by_severity[clash.severity].append(clash)

    # Summary
    print("\nSummary:")
    print("-" * 70)
    for severity in ClashSeverity:
        count = len(by_severity[severity])
        if count > 0:
            print(f"  {severity.value}: {count}")
    print(f"  TOTAL: {len(clashes)}")

    # Details
    for severity in ClashSeverity:
        if not by_severity[severity]:
            continue

        print(f"\n\n{'=' * 70}")
        print(f"{severity.value} CLASHES")
        print("=" * 70)

        for i, clash in enumerate(by_severity[severity], 1):
            print(f"\n[{i}] {clash.element_1_id} vs {clash.element_2_id}")
            print(f"    Type: {clash.element_2_type.value}")
            print(f"    Level: {clash.level}")
            print(f"    {clash.description}")
            print(f"    Location: ({clash.intersection_point.x:.1f}, "
                  f"{clash.intersection_point.y:.1f}, {clash.intersection_point.z:.1f})")

            if clash.recommendations:
                print("    Recommendations:")
                for rec in clash.recommendations:
                    print(f"      - {rec}")

    print()


# Example usage
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("CTR SYSTEM - CLASH DETECTION EXAMPLE")
    print("=" * 70)

    engine = ClashDetectionEngine()

    # Add rod runs (vertical cylinders)
    rods = [
        SpatialElement(
            element_id="RR-A-01",
            element_type=ElementType.ROD,
            geometry=Cylinder(
                start=Point3D(12.0, 6.0, 0.0),
                end=Point3D(12.0, 6.0, 47.5 * 12),  # 47.5 ft tall
                radius=0.875 / 2  # 7/8" diameter
            ),
            level=0,
            description="Rod run at Grid A, Left"
        ),
        SpatialElement(
            element_id="RR-A-02",
            element_type=ElementType.ROD,
            geometry=Cylinder(
                start=Point3D(12.0, 18.0, 0.0),
                end=Point3D(12.0, 18.0, 47.5 * 12),
                radius=0.75 / 2  # 3/4" diameter
            ),
            level=0,
            description="Rod run at Grid A, Right"
        ),
        SpatialElement(
            element_id="RR-B-01",
            element_type=ElementType.ROD,
            geometry=Cylinder(
                start=Point3D(36.0, 6.0, 0.0),
                end=Point3D(36.0, 6.0, 47.5 * 12),
                radius=1.0 / 2  # 1" diameter
            ),
            level=0,
            description="Rod run at Grid B, Left"
        ),
    ]

    for rod in rods:
        engine.add_element(rod)

    # Add MEP elements at various levels
    mep_elements = [
        # HVAC duct crossing near rod RR-A-01 at Level 3
        SpatialElement(
            element_id="HVAC-301",
            element_type=ElementType.HVAC_DUCT,
            geometry=Box(
                center=Point3D(12.5, 6.0, 28.0 * 12),  # Level 3
                width=24.0,  # 24" wide duct
                height=12.0,  # 12" tall duct
                depth=48.0   # 4' run
            ),
            level=3,
            description="24x12 Supply Duct"
        ),
        # Plumbing pipe near rod RR-A-02
        SpatialElement(
            element_id="PLMB-201",
            element_type=ElementType.PLUMBING_PIPE,
            geometry=Cylinder(
                start=Point3D(11.0, 18.0, 19.0 * 12),
                end=Point3D(13.5, 18.0, 19.0 * 12),
                radius=2.0  # 4" pipe
            ),
            level=2,
            description="4\" Waste Line"
        ),
        # Fire sprinkler main (direct conflict with RR-B-01)
        SpatialElement(
            element_id="FP-401",
            element_type=ElementType.FIRE_SPRINKLER,
            geometry=Cylinder(
                start=Point3D(30.0, 6.0, 37.5 * 12),
                end=Point3D(42.0, 6.0, 37.5 * 12),
                radius=1.5  # 3" main
            ),
            level=4,
            description="3\" Fire Main"
        ),
        # Electrical conduit (tight clearance)
        SpatialElement(
            element_id="ELEC-301",
            element_type=ElementType.ELECTRICAL_CONDUIT,
            geometry=Cylinder(
                start=Point3D(11.5, 5.0, 28.5 * 12),
                end=Point3D(11.5, 7.0, 28.5 * 12),
                radius=0.75  # 1.5" conduit
            ),
            level=3,
            description="1.5\" EMT Conduit"
        ),
        # Structural beam (OK clearance)
        SpatialElement(
            element_id="STR-201",
            element_type=ElementType.STRUCTURAL_BEAM,
            geometry=Box(
                center=Point3D(12.0, 10.0, 19.0 * 12),
                width=3.5,   # 2x beam
                height=11.25,  # 2x12
                depth=24.0
            ),
            level=2,
            description="2x12 Header"
        ),
    ]

    for elem in mep_elements:
        engine.add_element(elem)

    print(f"\nElements loaded:")
    print(f"  Rod runs: {len(rods)}")
    print(f"  MEP elements: {len(mep_elements)}")

    # Detect clashes
    print("\nRunning clash detection...")
    clashes = engine.detect_all_clashes(clearance_buffer=3.0)

    print_clash_report(clashes)

    # Export summary
    print("\n" + "=" * 70)
    print("CLASH SUMMARY BY ELEMENT")
    print("=" * 70)
    print(f"\n{'Rod Run':<12}{'Clashes':<10}{'Critical':<10}{'Major':<10}{'Minor'}")
    print("-" * 70)

    for rod in rods:
        rod_clashes = [c for c in clashes if c.element_1_id == rod.element_id]
        critical = sum(1 for c in rod_clashes if c.severity == ClashSeverity.CRITICAL)
        major = sum(1 for c in rod_clashes if c.severity == ClashSeverity.MAJOR)
        minor = sum(1 for c in rod_clashes if c.severity == ClashSeverity.MINOR)
        print(f"{rod.element_id:<12}{len(rod_clashes):<10}{critical:<10}{major:<10}{minor}")

    print()
