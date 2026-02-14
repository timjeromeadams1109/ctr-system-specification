# Section 6 — Revision Differencing Engine

## 6.1 Geometric Differencing Architecture

### 6.1.1 Diff Engine Overview

The revision differencing engine performs multi-dimensional comparison across geometry, metadata, structural properties, and derived calculations.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    REVISION DIFFERENCING ENGINE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐                      ┌──────────────┐                 │
│  │  BASELINE    │                      │  COMPARISON  │                 │
│  │  VERSION     │                      │  VERSION     │                 │
│  │  (Rev A)     │                      │  (Rev B)     │                 │
│  └──────┬───────┘                      └──────┬───────┘                 │
│         │                                      │                         │
│         ▼                                      ▼                         │
│  ┌──────────────────────────────────────────────────────┐               │
│  │              ENTITY CORRELATION ENGINE                │               │
│  │                                                       │               │
│  │  • ID-based matching (persistent IDs)                │               │
│  │  • Geometry-based matching (fuzzy)                   │               │
│  │  • Attribute-based matching (properties)             │               │
│  └──────────────────────────┬───────────────────────────┘               │
│                             │                                            │
│         ┌───────────────────┼───────────────────┐                       │
│         ▼                   ▼                   ▼                        │
│  ┌────────────┐     ┌────────────┐     ┌────────────┐                  │
│  │  GEOMETRY  │     │  METADATA  │     │ STRUCTURAL │                  │
│  │   DIFFER   │     │   DIFFER   │     │   DIFFER   │                  │
│  └─────┬──────┘     └─────┬──────┘     └─────┬──────┘                  │
│        │                  │                  │                          │
│        └──────────────────┼──────────────────┘                          │
│                           ▼                                              │
│              ┌────────────────────────┐                                 │
│              │   CHANGE AGGREGATOR    │                                 │
│              └────────────────────────┘                                 │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 6.2 Entity Correlation Engine

```python
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from enum import Enum

class MatchConfidence(Enum):
    EXACT = "EXACT"           # Same persistent ID
    HIGH = "HIGH"             # Strong geometry + attribute match
    MEDIUM = "MEDIUM"         # Partial match
    LOW = "LOW"               # Weak match
    NO_MATCH = "NO_MATCH"

@dataclass
class EntityMatch:
    """Matched entity pair between versions."""
    baseline_id: str
    comparison_id: str
    confidence: MatchConfidence
    match_score: float
    match_method: str
    geometry_delta: Optional[float] = None
    attribute_deltas: Dict[str, Tuple] = None

@dataclass
class CorrelationResult:
    """Results of entity correlation."""
    matched_pairs: List[EntityMatch]
    baseline_unmatched: List[str]  # Removed entities
    comparison_unmatched: List[str]  # Added entities
    ambiguous_matches: List[Tuple[str, List[str]]]


class EntityCorrelationEngine:
    """Correlate entities between drawing revisions."""

    def __init__(self, config: Dict = None):
        self.geometry_tolerance = config.get('geometry_tolerance_in', 0.5)
        self.min_match_score = config.get('min_match_score', 0.6)

    def correlate_entities(
        self,
        baseline_entities: Dict[str, Dict],
        comparison_entities: Dict[str, Dict],
        entity_type: str
    ) -> CorrelationResult:
        """Correlate entities between versions."""
        matched_pairs = []
        baseline_unmatched = set(baseline_entities.keys())
        comparison_unmatched = set(comparison_entities.keys())

        # Phase 1: Exact ID matching (persistent IDs)
        for base_id, base_entity in baseline_entities.items():
            persistent_id = base_entity.get('persistent_id')
            if persistent_id:
                for comp_id, comp_entity in comparison_entities.items():
                    if comp_entity.get('persistent_id') == persistent_id:
                        matched_pairs.append(EntityMatch(
                            baseline_id=base_id,
                            comparison_id=comp_id,
                            confidence=MatchConfidence.EXACT,
                            match_score=1.0,
                            match_method='PERSISTENT_ID'
                        ))
                        baseline_unmatched.discard(base_id)
                        comparison_unmatched.discard(comp_id)
                        break

        # Phase 2: Geometry-based matching for unmatched
        for base_id in list(baseline_unmatched):
            base_entity = baseline_entities[base_id]
            candidates = []

            for comp_id in comparison_unmatched:
                comp_entity = comparison_entities[comp_id]
                score = self._compute_match_score(base_entity, comp_entity, entity_type)
                if score >= self.min_match_score:
                    candidates.append((comp_id, score))

            if len(candidates) == 1:
                comp_id, score = candidates[0]
                matched_pairs.append(EntityMatch(
                    baseline_id=base_id,
                    comparison_id=comp_id,
                    confidence=self._score_to_confidence(score),
                    match_score=score,
                    match_method='GEOMETRY_ATTRIBUTE'
                ))
                baseline_unmatched.discard(base_id)
                comparison_unmatched.discard(comp_id)

        return CorrelationResult(
            matched_pairs=matched_pairs,
            baseline_unmatched=list(baseline_unmatched),
            comparison_unmatched=list(comparison_unmatched),
            ambiguous_matches=[]
        )
```

---

## 6.3 Property Differencing

```python
class ChangeType(Enum):
    ADDED = "ADDED"
    REMOVED = "REMOVED"
    MODIFIED = "MODIFIED"
    RELOCATED = "RELOCATED"
    UNCHANGED = "UNCHANGED"

class ChangeImpact(Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass
class PropertyChange:
    """Change to a single property."""
    property_name: str
    baseline_value: Any
    comparison_value: Any
    change_type: ChangeType
    change_magnitude: Optional[float] = None
    impact: ChangeImpact = ChangeImpact.LOW
    requires_recalc: bool = False

@dataclass
class EntityChange:
    """All changes to an entity between versions."""
    entity_id: str
    entity_type: str
    change_type: ChangeType
    property_changes: List[PropertyChange]
    geometry_changed: bool = False
    structural_impact: ChangeImpact = ChangeImpact.NONE
    cost_impact: ChangeImpact = ChangeImpact.NONE


class PropertyDiffer:
    """Compare properties between entity versions."""

    STRUCTURAL_PROPERTIES = {
        'SHEAR_WALL': ['length_ft', 'sheathing_type', 'nail_spacing_edge', 'unit_shear_plf'],
        'ROD_RUN': ['rod_diameter_in', 'rod_grade', 'demand_tension_lb', 'levels_served'],
        'HOLDOWN': ['model', 'allowable_tension_lb'],
        'ANCHOR': ['embed_depth_in', 'diameter_in', 'anchor_type']
    }

    COST_PROPERTIES = {
        'ROD_RUN': ['rod_diameter_in', 'total_length_ft', 'rod_grade'],
        'HOLDOWN': ['model'],
        'ANCHOR': ['anchor_type', 'model']
    }

    def diff_entity(
        self,
        baseline: Dict,
        comparison: Dict,
        entity_type: str
    ) -> EntityChange:
        """Compute differences between versions."""
        property_changes = []

        all_keys = set(baseline.keys()) | set(comparison.keys())
        exclude_keys = {'entity_id', 'persistent_id', 'created_at', 'modified_at'}
        all_keys -= exclude_keys

        for key in all_keys:
            base_val = baseline.get(key)
            comp_val = comparison.get(key)

            if base_val != comp_val:
                change = self._create_property_change(key, base_val, comp_val, entity_type)
                property_changes.append(change)

        structural_impact = self._assess_structural_impact(property_changes, entity_type)
        cost_impact = self._assess_cost_impact(property_changes, entity_type)

        return EntityChange(
            entity_id=baseline.get('entity_id') or comparison.get('entity_id'),
            entity_type=entity_type,
            change_type=ChangeType.MODIFIED if property_changes else ChangeType.UNCHANGED,
            property_changes=property_changes,
            structural_impact=structural_impact,
            cost_impact=cost_impact
        )
```

---

## 6.4 ID Persistence Method

```python
class PersistentIDManager:
    """Manage persistent identifiers across revisions."""

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.id_registry: Dict[str, Dict] = {}
        self.geometry_index: Dict[str, str] = {}

    def generate_persistent_id(
        self,
        entity_type: str,
        entity_data: Dict
    ) -> str:
        """Generate new persistent ID for entity."""
        geom_hash = self._compute_geometry_hash(entity_type, entity_data)

        # Check if ID exists for this geometry
        if geom_hash in self.geometry_index:
            return self.geometry_index[geom_hash]

        # Generate new ID
        project_hash = hashlib.md5(self.project_id.encode()).hexdigest()[:8]
        sequence = len([k for k in self.id_registry if k.startswith(f"{entity_type}-")])

        persistent_id = f"{entity_type}-{project_hash}-{sequence:06d}"

        self.id_registry[persistent_id] = {
            'created_at': datetime.utcnow().isoformat(),
            'entity_type': entity_type,
            'geometry_hash': geom_hash,
            'version_history': []
        }

        self.geometry_index[geom_hash] = persistent_id
        return persistent_id

    def _compute_geometry_hash(self, entity_type: str, data: Dict) -> str:
        """Compute hash of geometry for matching."""
        precision = 1  # 0.1" precision

        if entity_type == 'SHEAR_WALL':
            key_data = (
                round(data.get('start_x', 0) * precision),
                round(data.get('start_y', 0) * precision),
                round(data.get('end_x', 0) * precision),
                round(data.get('end_y', 0) * precision),
                data.get('level', 0)
            )
        elif entity_type == 'ROD_RUN':
            key_data = (
                round(data.get('x_position', 0) * precision),
                round(data.get('y_position', 0) * precision),
                data.get('direction', ''),
                data.get('grid_location', '')
            )
        else:
            key_data = tuple(sorted(data.items()))

        hash_input = f"{entity_type}:{key_data}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]
```

---

## 6.5 Cost and Material Delta Calculation

```python
@dataclass
class MaterialDelta:
    """Change in material quantities."""
    item_code: str
    description: str
    category: str
    baseline_qty: float
    comparison_qty: float
    delta_qty: float
    unit: str
    delta_weight_lb: float
    delta_cost: float

    @property
    def change_percent(self) -> float:
        if self.baseline_qty == 0:
            return float('inf') if self.comparison_qty > 0 else 0
        return (self.delta_qty / self.baseline_qty) * 100


class MaterialDeltaCalculator:
    """Calculate material quantity changes."""

    ROD_PROPERTIES = {
        0.625: {'weight_per_ft': 1.04, 'cost_per_ft': 2.50},
        0.750: {'weight_per_ft': 1.50, 'cost_per_ft': 3.25},
        0.875: {'weight_per_ft': 2.04, 'cost_per_ft': 4.00},
        1.000: {'weight_per_ft': 2.67, 'cost_per_ft': 5.00},
        1.125: {'weight_per_ft': 3.38, 'cost_per_ft': 6.25},
        1.250: {'weight_per_ft': 4.17, 'cost_per_ft': 7.50},
        1.375: {'weight_per_ft': 5.05, 'cost_per_ft': 9.00},
        1.500: {'weight_per_ft': 6.01, 'cost_per_ft': 11.00}
    }

    def compute_deltas(self) -> Dict[str, MaterialDelta]:
        """Compute material quantity deltas."""
        deltas = {}
        all_codes = set(self.baseline_quantities.keys()) | set(self.comparison_quantities.keys())

        for code in all_codes:
            base_qty = self.baseline_quantities.get(code)
            comp_qty = self.comparison_quantities.get(code)

            ref = base_qty or comp_qty
            baseline_val = base_qty.quantity if base_qty else 0
            comparison_val = comp_qty.quantity if comp_qty else 0
            delta_val = comparison_val - baseline_val

            deltas[code] = MaterialDelta(
                item_code=code,
                description=ref.description,
                category=ref.category.value,
                baseline_qty=baseline_val,
                comparison_qty=comparison_val,
                delta_qty=delta_val,
                unit=ref.unit,
                delta_weight_lb=delta_val * ref.unit_weight_lb,
                delta_cost=delta_val * ref.unit_cost
            )

        return deltas
```
