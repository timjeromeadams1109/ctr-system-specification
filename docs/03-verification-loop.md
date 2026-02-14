# Section 3 — Self-Verification Loop

## 3.1 Verification Architecture

### 3.1.1 Dual-Pass Design Philosophy

The self-verification system implements a mandatory two-pass calculation process where independent computational paths must converge within defined tolerance thresholds before design acceptance.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SELF-VERIFICATION LOOP                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────────┐         ┌───────────────┐                       │
│  │   PASS 1      │         │   PASS 2      │                       │
│  │  Rod Design   │         │  Structural   │                       │
│  │    Agent      │         │  Audit Agent  │                       │
│  └───────┬───────┘         └───────┬───────┘                       │
│          │                         │                                │
│          ▼                         ▼                                │
│  ┌───────────────┐         ┌───────────────┐                       │
│  │ Primary       │         │ Independent   │                       │
│  │ Calculations  │         │ Recalculation │                       │
│  │               │         │               │                       │
│  │ • Load path   │         │ • Fresh load  │                       │
│  │ • Tensions    │         │   extraction  │                       │
│  │ • Rod sizing  │         │ • Alternate   │                       │
│  │ • Shrinkage   │         │   algorithms  │                       │
│  └───────┬───────┘         └───────┬───────┘                       │
│          │                         │                                │
│          └──────────┬──────────────┘                                │
│                     ▼                                               │
│          ┌───────────────────┐                                      │
│          │   COMPARATOR      │                                      │
│          │                   │                                      │
│          │ Δ ≤ tolerance?    │                                      │
│          └─────────┬─────────┘                                      │
│                    │                                                │
│          ┌────────┴────────┐                                       │
│          ▼                  ▼                                       │
│    ┌──────────┐      ┌──────────┐                                  │
│    │  PASS    │      │  FAIL    │                                  │
│    │          │      │          │                                  │
│    │ Continue │      │ Escalate │                                  │
│    │ to output│      │ & Re-run │                                  │
│    └──────────┘      └──────────┘                                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.1.2 Pass 1 — Primary Rod Design

The Rod Design Agent (RDA) performs initial calculations using the standard methodology:

```python
from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class PrimaryDesignResult:
    """Results from Pass 1 primary design."""
    rod_run_id: str
    input_hash: str

    # Calculated values
    overturning_moments: Dict[int, float]  # level -> M_ot (ft-lb)
    tension_demands: Dict[int, float]  # level -> T (lb)
    cumulative_tensions: Dict[int, float]  # level -> T_cumulative (lb)
    max_tension: float

    # Design selections
    selected_diameter: float
    rod_grade: str
    allowable_tension: float
    utilization_ratio: float

    # Shrinkage analysis
    shrinkage_by_level: Dict[int, float]
    total_shrinkage: float
    rod_elongation: float
    net_shortening: float
    take_up_model: Optional[str]

    # Intermediate values for audit
    calculation_details: Dict = field(default_factory=dict)
```

### 3.1.3 Pass 2 — Independent Structural Audit

The Structural Audit Agent (SAuA) performs completely independent recalculation:

```python
class StructuralAuditEngine:
    """Independent structural verification engine."""

    def perform_audit(
        self,
        primary_result: PrimaryDesignResult,
        raw_inputs: Dict
    ) -> 'AuditResult':
        """
        Perform independent verification of primary design.

        Steps:
        1. Recompute overturning moments from raw forces
        2. Recompute tension demands independently
        3. Recompute cumulative tensions
        4. Verify rod selection adequacy
        5. Recompute shrinkage
        6. Recompute rod elongation
        7. Compare with primary results
        8. Verify code compliance
        """
        # Implementation performs all calculations from scratch
        pass
```

---

## 3.2 Tolerance Thresholds

### 3.2.1 Numerical Tolerance Definitions

```python
TOLERANCE_THRESHOLDS = {
    # Force-related tolerances
    'tension_percent': 2.0,          # Maximum 2% difference
    'tension_absolute_lb': 500,      # Or 500 lb absolute
    'shear_percent': 2.0,
    'moment_percent': 2.0,

    # Geometry-related tolerances
    'length_in': 0.5,                # Maximum 0.5" difference
    'length_percent': 1.0,
    'position_in': 0.25,

    # Material property tolerances
    'shrinkage_in': 0.1,             # Maximum 0.1" difference
    'shrinkage_percent': 5.0,
    'elongation_in': 0.05,

    # Utilization tolerances
    'utilization_ratio': 0.02,       # Maximum 0.02 difference

    # Code compliance tolerances
    'capacity_percent': 1.0,
    'embed_depth_in': 0.5,
}
```

### 3.2.2 Tolerance Application Matrix

| Parameter | Percent Tolerance | Absolute Tolerance | Governing |
|-----------|-------------------|-------------------|-----------|
| Tension Force | 2.0% | 500 lb | Lesser |
| Shear Force | 2.0% | 200 lb | Lesser |
| Overturning Moment | 2.0% | 1000 ft-lb | Lesser |
| Wall Length | 1.0% | 0.5" | Lesser |
| Rod Length | 1.0% | 1.0" | Lesser |
| Shrinkage | 5.0% | 0.1" | Lesser |
| Rod Elongation | 5.0% | 0.05" | Lesser |
| Utilization Ratio | N/A | 0.02 | Absolute |
| Embed Depth | 5.0% | 0.5" | Lesser |

---

## 3.3 Audit Verification Checks

### 3.3.1 Force Recalculation Verification

```python
class ForceVerificationEngine:
    """Independent force recalculation for audit."""

    def verify_overturning_moment(
        self,
        wall_id: str,
        primary_moment: float,
        raw_inputs: Dict
    ) -> Dict:
        """
        Verify overturning moment calculation.
        Uses ASCE 7-22 §12.8.5 methodology.
        """
        wall = raw_inputs['walls'][wall_id]
        level = wall['level']

        # Get seismic forces
        Fx = raw_inputs['seismic_forces'].get(level, {}).get('Fx_lb', 0)
        floor_height = raw_inputs['floor_heights'].get(level, 10.0)

        # Calculate overturning
        audit_moment = Fx * floor_height

        # Compare with tolerance
        return {
            'wall_id': wall_id,
            'primary_moment_ft_lb': primary_moment,
            'audit_moment_ft_lb': audit_moment,
            'within_tolerance': abs(primary_moment - audit_moment) / primary_moment < 0.02,
            'code_reference': 'ASCE 7-22 §12.8.5'
        }
```

### 3.3.2 Anchorage Verification

```python
class AnchorageVerificationEngine:
    """Verify foundation anchorage design."""

    def verify_embed_depth(
        self,
        anchor_id: str,
        primary_embed: float,
        raw_inputs: Dict
    ) -> Dict:
        """
        Verify anchor embedment meets code requirements.
        Per ACI 318-19 Chapter 17.
        """
        anchor = raw_inputs['anchors'].get(anchor_id, {})
        rod_diameter = anchor.get('rod_diameter_in', 1.0)

        # Minimum embed per ACI 318: 12d or 6", whichever greater
        min_embed = max(12 * rod_diameter, 6)

        return {
            'anchor_id': anchor_id,
            'primary_embed_in': primary_embed,
            'required_embed_in': min_embed,
            'adequate': primary_embed >= min_embed,
            'code_reference': 'ACI 318-19 §17.4.2'
        }

    def verify_plate_bearing(
        self,
        plate_id: str,
        bearing_stress: float,
        raw_inputs: Dict
    ) -> Dict:
        """
        Verify bearing plate stress on wood member.
        Per NDS 2024 §3.10.
        """
        plate = raw_inputs['bearing_plates'].get(plate_id, {})
        wood_species = plate.get('wood_species', 'DF_L')

        # Base Fc_perp values (ASD)
        FC_PERP = {'DF_L': 625, 'SPF': 425, 'SYP': 565, 'HEM_FIR': 405}
        Fc_perp = FC_PERP.get(wood_species, 500)

        return {
            'plate_id': plate_id,
            'bearing_stress_psi': bearing_stress,
            'allowable_psi': Fc_perp,
            'adequate': bearing_stress <= Fc_perp,
            'code_reference': 'NDS 2024 §3.10'
        }
```

### 3.3.3 Collector Continuity Verification

```python
class CollectorVerificationEngine:
    """Verify collector element continuity."""

    def verify_collector_capacity(
        self,
        collector_id: str,
        raw_inputs: Dict
    ) -> Dict:
        """
        Verify collector has adequate capacity per ASCE 7.
        Collectors in SDC D,E,F must be designed for Ωo.
        """
        collector = raw_inputs['collectors'].get(collector_id, {})
        sdc = raw_inputs.get('seismic_design_category', 'D')

        axial_demand = collector.get('axial_demand_lb', 0)
        axial_capacity = collector.get('axial_capacity_lb', 0)

        # Overstrength factor
        omega_0 = 3.0 if sdc in ['D', 'E', 'F'] else 1.0
        amplified_demand = axial_demand * omega_0

        return {
            'collector_id': collector_id,
            'amplified_demand_lb': amplified_demand,
            'capacity_lb': axial_capacity,
            'adequate': axial_capacity >= amplified_demand,
            'code_reference': 'ASCE 7-22 §12.10.2'
        }
```

---

## 3.4 Discrepancy Handling

### 3.4.1 Discrepancy Classification

```python
from enum import Enum

class DiscrepancySeverity(Enum):
    MINOR = "MINOR"           # < 2% difference, informational
    MODERATE = "MODERATE"     # 2-5% difference, review recommended
    CRITICAL = "CRITICAL"     # > 5% difference, must resolve
    BLOCKING = "BLOCKING"     # Calculation error, cannot proceed

class DiscrepancyAction(Enum):
    LOG_ONLY = "LOG_ONLY"
    FLAG_FOR_REVIEW = "FLAG_FOR_REVIEW"
    RERUN_PRIMARY = "RERUN_PRIMARY"
    ESCALATE_TO_PE = "ESCALATE_TO_PE"
    HALT_PROCESSING = "HALT_PROCESSING"
```

### 3.4.2 Discrepancy Resolution Workflow

```python
class DiscrepancyHandler:
    """Handle discrepancies between primary and audit calculations."""

    def __init__(self, config: Dict):
        self.max_reruns = config.get('max_reruns', 2)
        self.rerun_count = 0

    def classify_severity(
        self,
        parameter: str,
        difference_percent: float
    ) -> DiscrepancySeverity:
        """Classify discrepancy severity."""
        if difference_percent > 5.0:
            return DiscrepancySeverity.CRITICAL
        elif difference_percent > 2.0:
            return DiscrepancySeverity.MODERATE
        else:
            return DiscrepancySeverity.MINOR

    def determine_action(
        self,
        severity: DiscrepancySeverity
    ) -> DiscrepancyAction:
        """Determine required action."""
        if severity == DiscrepancySeverity.CRITICAL:
            if self.rerun_count < self.max_reruns:
                return DiscrepancyAction.RERUN_PRIMARY
            return DiscrepancyAction.ESCALATE_TO_PE
        elif severity == DiscrepancySeverity.MODERATE:
            return DiscrepancyAction.FLAG_FOR_REVIEW
        else:
            return DiscrepancyAction.LOG_ONLY
```

---

## 3.5 Audit Conflict Logging

### 3.5.1 Conflict Log Schema

```json
{
  "log_id": "ALOG-20240215-143022",
  "project_id": "string",
  "timestamp": "ISO8601",
  "conflicts": [
    {
      "conflict_id": "CONF-0001",
      "type": "VALUE_MISMATCH",
      "element_id": "RR-NS-A-L",
      "parameter": "max_tension_lb",
      "primary_value": 25000,
      "audit_value": 25800,
      "difference_percent": 3.2,
      "severity": "MODERATE",
      "resolution": "FLAGGED_FOR_REVIEW"
    }
  ],
  "summary": {
    "total_conflicts": 1,
    "by_severity": {"MODERATE": 1},
    "pe_review_required": false
  }
}
```

### 3.5.2 Chain Integrity Verification

```python
class AuditTrailManager:
    """Manage immutable audit trail with hash chain."""

    def verify_chain_integrity(self) -> Dict:
        """Verify integrity of entire audit chain."""
        events = self.storage.get_all_events(self.project_id)
        issues = []
        expected_prev_hash = "GENESIS"

        for event in events:
            # Verify hash chain link
            if event.previous_event_hash != expected_prev_hash:
                issues.append({
                    'event_id': event.event_id,
                    'issue': 'CHAIN_BREAK'
                })

            # Verify event hash
            computed = event.compute_hash()
            if event.event_hash != computed:
                issues.append({
                    'event_id': event.event_id,
                    'issue': 'HASH_MISMATCH'
                })

            expected_prev_hash = event.event_hash

        return {
            'valid': len(issues) == 0,
            'events_checked': len(events),
            'issues': issues
        }
```
