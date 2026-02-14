# Section 5 — Clash Detection Engine

## 5.1 Geometric Intersection Mathematics

### 5.1.1 3D Bounding Volume Representation

**Axis-Aligned Bounding Box (AABB):**

$$AABB = \{(x, y, z) : x_{min} \leq x \leq x_{max}, y_{min} \leq y \leq y_{max}, z_{min} \leq z \leq z_{max}\}$$

**Oriented Bounding Box (OBB):**

$$OBB = \{C + r_1 \cdot \vec{u_1} + r_2 \cdot \vec{u_2} + r_3 \cdot \vec{u_3} : -1 \leq r_i \leq 1\}$$

Where:
- $C$ = Center point
- $\vec{u_i}$ = Orthonormal basis vectors
- $r_i$ = Half-extent along each axis

### 5.1.2 Parametric Rod Cylinder

A continuous threaded rod is represented as a cylinder:

$$\text{Cylinder}(P_1, P_2, r) = \{P : d(P, \overline{P_1P_2}) \leq r\}$$

**Distance from point to line segment:**

$$d(P, \overline{P_1P_2}) = \begin{cases}
\|P - P_1\| & \text{if } t \leq 0 \\
\|P - P_2\| & \text{if } t \geq 1 \\
\|P - (P_1 + t \cdot \vec{v})\| & \text{otherwise}
\end{cases}$$

Where: $t = \frac{(P - P_1) \cdot \vec{v}}{\|\vec{v}\|^2}$ and $\vec{v} = P_2 - P_1$

---

## 5.2 Cylinder-Cylinder Intersection

```python
import numpy as np
from typing import Tuple, Optional

def cylinder_cylinder_intersection(
    cyl1_p1: np.ndarray,
    cyl1_p2: np.ndarray,
    cyl1_radius: float,
    cyl2_p1: np.ndarray,
    cyl2_p2: np.ndarray,
    cyl2_radius: float
) -> Tuple[bool, Optional[float], Optional[np.ndarray]]:
    """
    Detect intersection between two finite cylinders.

    Returns:
        Tuple of (intersects, penetration_depth, intersection_point)
    """
    # Direction vectors
    d1 = cyl1_p2 - cyl1_p1
    d2 = cyl2_p2 - cyl2_p1

    len1 = np.linalg.norm(d1)
    len2 = np.linalg.norm(d2)

    if len1 == 0 or len2 == 0:
        return (False, None, None)

    # Unit direction vectors
    u1 = d1 / len1
    u2 = d2 / len2

    # Find closest points between axis lines
    w = cyl1_p1 - cyl2_p1
    a = np.dot(u1, u1)  # = 1
    b = np.dot(u1, u2)
    c = np.dot(u2, u2)  # = 1
    d = np.dot(u1, w)
    e = np.dot(u2, w)

    denom = a * c - b * b

    if abs(denom) < 1e-10:
        # Lines are parallel
        t1, t2 = 0, -e / c if c != 0 else 0
    else:
        t1 = (b * e - c * d) / denom
        t2 = (a * e - b * d) / denom

    # Clamp to segment bounds
    t1 = max(0, min(1, t1 / len1)) * len1
    t2 = max(0, min(1, t2 / len2)) * len2

    # Closest points on each axis
    closest1 = cyl1_p1 + (t1 / len1) * d1 if len1 > 0 else cyl1_p1
    closest2 = cyl2_p1 + (t2 / len2) * d2 if len2 > 0 else cyl2_p1

    # Distance between closest points
    distance = np.linalg.norm(closest1 - closest2)
    combined_radius = cyl1_radius + cyl2_radius

    if distance < combined_radius:
        penetration = combined_radius - distance
        intersection_point = (closest1 + closest2) / 2
        return (True, penetration, intersection_point)

    return (False, None, None)
```

---

## 5.3 Cylinder-Box Intersection

```python
def cylinder_box_intersection(
    cyl_p1: np.ndarray,
    cyl_p2: np.ndarray,
    cyl_radius: float,
    box_min: np.ndarray,
    box_max: np.ndarray
) -> Tuple[bool, Optional[float], Optional[np.ndarray]]:
    """
    Detect intersection between cylinder and axis-aligned box.
    Used for rod-to-beam/header clash detection.
    """
    d = cyl_p2 - cyl_p1
    length = np.linalg.norm(d)

    if length == 0:
        # Point cylinder
        expanded_min = box_min - cyl_radius
        expanded_max = box_max + cyl_radius
        inside = np.all(cyl_p1 >= expanded_min) and np.all(cyl_p1 <= expanded_max)
        return (inside, cyl_radius if inside else None, cyl_p1 if inside else None)

    # Sample points along cylinder axis
    num_samples = max(10, int(length / cyl_radius))

    for i in range(num_samples + 1):
        t = i / num_samples
        point = cyl_p1 + t * d

        # Find closest point on box surface
        closest = np.clip(point, box_min, box_max)
        dist = np.linalg.norm(point - closest)

        if dist < cyl_radius:
            penetration = cyl_radius - dist
            return (True, penetration, closest)

    return (False, None, None)
```

---

## 5.4 Spatial Indexing with R-Tree

```python
from rtree import index
from typing import List, Dict, Generator

class SpatialClashIndex:
    """R-tree based spatial index for clash detection."""

    def __init__(self):
        props = index.Property()
        props.dimension = 3
        props.fill_factor = 0.7
        props.leaf_capacity = 100

        self.idx = index.Index(properties=props)
        self.elements: Dict[int, Dict] = {}
        self.next_id = 0

    def insert_element(
        self,
        element_id: str,
        element_type: str,
        bounds: Tuple[float, float, float, float, float, float],
        geometry_data: Dict
    ) -> int:
        """Insert element into spatial index."""
        internal_id = self.next_id
        self.next_id += 1

        self.elements[internal_id] = {
            'element_id': element_id,
            'element_type': element_type,
            'bounds': bounds,
            'geometry': geometry_data
        }

        self.idx.insert(internal_id, bounds)
        return internal_id

    def query_potential_clashes(
        self,
        bounds: Tuple,
        exclude_types: List[str] = None
    ) -> Generator[Dict, None, None]:
        """Query elements that potentially clash with bounds."""
        exclude_types = exclude_types or []
        hits = self.idx.intersection(bounds)

        for internal_id in hits:
            element = self.elements.get(internal_id)
            if element and element['element_type'] not in exclude_types:
                yield element

    def find_all_rod_clashes(
        self,
        clearance_in: float = 1.0
    ) -> List[Dict]:
        """Find all clashes involving rod elements."""
        clashes = []

        rods = [
            (iid, el) for iid, el in self.elements.items()
            if el['element_type'] == 'ROD'
        ]

        for rod_iid, rod_el in rods:
            bounds = rod_el['bounds']
            expanded = (
                bounds[0] - clearance_in,
                bounds[1] - clearance_in,
                bounds[2] - clearance_in,
                bounds[3] + clearance_in,
                bounds[4] + clearance_in,
                bounds[5] + clearance_in
            )

            for other in self.query_potential_clashes(expanded, ['ROD']):
                clash = self._check_rod_element_clash(rod_el, other, clearance_in)
                if clash:
                    clashes.append(clash)

        return clashes
```

---

## 5.5 Clearance Requirements

### 5.5.1 Minimum Clearance by Element Type

| Element Type | Clearance from Rod | Rationale |
|--------------|-------------------|-----------|
| HVAC Duct | 2.0" | Installation access |
| Plumbing Pipe | 1.5" | Insulation + access |
| Electrical Conduit | 1.0" | Bending radius |
| Structural Beam | 0.5" | Field tolerance |
| Fire Sprinkler | 2.0" | Code requirement |
| Cable Tray | 1.5" | Access + expansion |

### 5.5.2 Severity Classification

```python
class ClashSeverityClassifier:
    """Classify clash severity and generate recommendations."""

    def classify(
        self,
        penetration: float,
        element_type: str,
        is_flexible: bool = False
    ) -> Dict:
        """Classify clash severity."""
        required_clearance = self.config.get_clearance(element_type)
        actual_clearance = -penetration

        if penetration > 0:
            severity = 'CRITICAL'
            description = f"Hard interference: {penetration:.2f}\" overlap"
        elif actual_clearance < required_clearance:
            clearance_violation = required_clearance - actual_clearance
            severity = 'MAJOR' if clearance_violation > required_clearance * 0.5 else 'MINOR'
            description = f"Clearance violation: {actual_clearance:.2f}\" vs {required_clearance:.2f}\" required"
        else:
            severity = 'WARNING'
            description = f"Near clearance limit"

        return {
            'severity': severity,
            'description': description,
            'penetration_in': penetration,
            'required_clearance_in': required_clearance,
            'recommendations': self._generate_recommendations(severity, element_type)
        }
```

---

## 5.6 Resolution Recommendations

```python
def _generate_recommendations(
    self,
    severity: str,
    element_type: str
) -> List[Dict]:
    """Generate resolution recommendations."""
    recommendations = []

    if severity == 'CRITICAL':
        recommendations.append({
            'option_id': 'RELOCATE_MEP',
            'description': f'Relocate {element_type} to clear rod path',
            'feasibility': 'MODERATE',
            'responsible_trade': self._get_trade(element_type),
            'cost_impact': 'LOW'
        })

        recommendations.append({
            'option_id': 'RELOCATE_ROD',
            'description': 'Relocate rod run (requires structural review)',
            'feasibility': 'DIFFICULT',
            'responsible_trade': 'STRUCTURAL',
            'cost_impact': 'MEDIUM'
        })

    elif severity == 'MAJOR':
        recommendations.append({
            'option_id': 'INCREASE_CLEARANCE',
            'description': f'Adjust {element_type} routing',
            'feasibility': 'EASY',
            'responsible_trade': self._get_trade(element_type),
            'cost_impact': 'NONE'
        })

    return recommendations
```
