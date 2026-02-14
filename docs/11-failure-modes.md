# Section 11 — Failure Modes and Mitigation

## 11.1 Drawing Interpretation Failures

### 11.1.1 Scale Detection Failure

```python
from dataclasses import dataclass
from typing import List, Optional, Dict
from enum import Enum

class FailureCategory(Enum):
    DRAWING_INTERPRETATION = "DRAWING_INTERPRETATION"
    GEOMETRY_EXTRACTION = "GEOMETRY_EXTRACTION"
    STRUCTURAL_ANALYSIS = "STRUCTURAL_ANALYSIS"
    CODE_COMPLIANCE = "CODE_COMPLIANCE"
    COORDINATION = "COORDINATION"
    DATA_INTEGRITY = "DATA_INTEGRITY"

class FailureSeverity(Enum):
    WARNING = "WARNING"           # Continue with caution
    ERROR = "ERROR"               # Requires resolution
    CRITICAL = "CRITICAL"         # Blocks processing
    FATAL = "FATAL"               # System failure

@dataclass
class FailureMode:
    """Definition of a failure mode."""
    failure_id: str
    category: FailureCategory
    severity: FailureSeverity
    description: str
    detection_logic: str
    impact: str
    mitigation: List[str]
    confidence_penalty: float  # 0-1 reduction

FAILURE_MODES = {
    'FM-DI-001': FailureMode(
        failure_id='FM-DI-001',
        category=FailureCategory.DRAWING_INTERPRETATION,
        severity=FailureSeverity.CRITICAL,
        description="Scale detection failure",
        detection_logic="""
            - No scale annotation found in title block
            - Multiple conflicting scales detected
            - Scale factor results in unrealistic dimensions
              (e.g., walls < 1ft or > 100ft)
        """,
        impact="""
            All geometry calculations will be incorrect.
            Rod lengths, spacing, and material quantities invalid.
        """,
        mitigation=[
            "Search for scale text patterns: '1/4\" = 1\\'', 'SCALE: 1:48', etc.",
            "Measure known dimension (door width = 3'-0\") to derive scale",
            "Compare dimension callouts to measured lengths",
            "Prompt user for manual scale input with preview",
            "Cross-reference with other drawings in set"
        ],
        confidence_penalty=0.5
    ),

    'FM-DI-002': FailureMode(
        failure_id='FM-DI-002',
        category=FailureCategory.DRAWING_INTERPRETATION,
        severity=FailureSeverity.ERROR,
        description="Missing or illegible title block",
        detection_logic="""
            - Title block region empty or corrupt
            - OCR confidence < 60% on title block text
            - Required fields (drawing number, date, revision) not found
        """,
        impact="""
            Cannot establish drawing metadata.
            Revision tracking compromised.
        """,
        mitigation=[
            "Apply image enhancement (contrast, deskew)",
            "Use alternate OCR engine",
            "Extract metadata from filename",
            "Prompt user for manual entry",
            "Flag for PE review"
        ],
        confidence_penalty=0.15
    ),

    'FM-DI-003': FailureMode(
        failure_id='FM-DI-003',
        category=FailureCategory.DRAWING_INTERPRETATION,
        severity=FailureSeverity.ERROR,
        description="Grid system not detected",
        detection_logic="""
            - No grid line patterns found
            - Grid labels not associated with lines
            - Grid spacing inconsistent (>20% variation)
        """,
        impact="""
            Cannot establish coordinate reference system.
            Rod placement descriptions will lack grid references.
        """,
        mitigation=[
            "Search for typical grid patterns (parallel lines with bubble callouts)",
            "Use wall intersections to infer grid locations",
            "Allow manual grid definition overlay",
            "Use relative coordinates with dimension callouts"
        ],
        confidence_penalty=0.2
    )
}
```

### 11.1.2 Layer Interpretation Failures

```python
LAYER_FAILURE_MODES = {
    'FM-DI-010': FailureMode(
        failure_id='FM-DI-010',
        category=FailureCategory.DRAWING_INTERPRETATION,
        severity=FailureSeverity.WARNING,
        description="Non-standard layer naming",
        detection_logic="""
            - Layer names don't match AIA CAD Layer Guidelines
            - Shear wall layer not identifiable
            - Mixed content on single layers
        """,
        impact="""
            Automated layer filtering unreliable.
            May include/exclude wrong elements.
        """,
        mitigation=[
            "Apply heuristic layer classification based on content",
            "Use geometry properties (line weight, color) for classification",
            "Present layer mapping interface to user",
            "Learn from user corrections for future projects"
        ],
        confidence_penalty=0.1
    ),

    'FM-DI-011': FailureMode(
        failure_id='FM-DI-011',
        category=FailureCategory.DRAWING_INTERPRETATION,
        severity=FailureSeverity.ERROR,
        description="Critical layers missing",
        detection_logic="""
            - Expected structural layers not present
            - Shear wall schedule not linked
            - Holdown schedule not found
        """,
        impact="""
            Cannot perform complete structural analysis.
            Design may be incomplete.
        """,
        mitigation=[
            "Search all layers for structural content",
            "Check for external references (xrefs)",
            "Request additional drawings from user",
            "Mark affected elements as 'UNVERIFIED'"
        ],
        confidence_penalty=0.25
    )
}
```

---

## 11.2 Geometry Extraction Failures

### 11.2.1 Shear Wall Detection Failures

```python
SHEAR_WALL_FAILURE_MODES = {
    'FM-GE-001': FailureMode(
        failure_id='FM-GE-001',
        category=FailureCategory.GEOMETRY_EXTRACTION,
        severity=FailureSeverity.CRITICAL,
        description="Ambiguous shear wall identification",
        detection_logic="""
            - Wall segment could be shear or partition
            - No schedule correlation available
            - Sheathing notation unclear
            - Multiple interpretations possible
        """,
        impact="""
            Rod system may be designed for wrong walls.
            Structural inadequacy or over-design.
        """,
        mitigation=[
            "Check for sheathing notation (OSB, PLY, GYP)",
            "Look for holdown symbols at wall ends",
            "Cross-reference with shear wall schedule",
            "Flag for engineer review with options",
            "Apply conservative assumption (treat as shear wall)"
        ],
        confidence_penalty=0.3
    ),

    'FM-GE-002': FailureMode(
        failure_id='FM-GE-002',
        category=FailureCategory.GEOMETRY_EXTRACTION,
        severity=FailureSeverity.ERROR,
        description="Missing holdown at shear wall",
        detection_logic="""
            - Shear wall identified but no holdown symbol found
            - Holdown symbol present but not associated with wall
            - Schedule shows holdown but not shown on plan
        """,
        impact="""
            Incomplete load path definition.
            Rod run endpoint undefined.
        """,
        mitigation=[
            "Search expanded area around wall ends",
            "Check for alternate holdown representations",
            "Cross-reference with holdown schedule",
            "Place default holdown at wall ends (flagged)",
            "Alert user for verification"
        ],
        confidence_penalty=0.2
    ),

    'FM-GE-003': FailureMode(
        failure_id='FM-GE-003',
        category=FailureCategory.GEOMETRY_EXTRACTION,
        severity=FailureSeverity.WARNING,
        description="Shear wall stack misalignment",
        detection_logic="""
            - Walls on adjacent levels not within tolerance
            - Offset > 12 inches between levels
            - Load path discontinuity detected
        """,
        impact="""
            Rod run may require offset or multiple segments.
            Additional structural considerations needed.
        """,
        mitigation=[
            "Verify offset is intentional vs drawing error",
            "Calculate collector requirements if offset",
            "Flag for structural review",
            "Consider alternative rod routing"
        ],
        confidence_penalty=0.15
    ),

    'FM-GE-004': FailureMode(
        failure_id='FM-GE-004',
        category=FailureCategory.GEOMETRY_EXTRACTION,
        severity=FailureSeverity.ERROR,
        description="Wall length discrepancy",
        detection_logic="""
            - Measured length differs from schedule by >6 inches
            - Dimension callout conflicts with scaled measurement
            - Multiple dimension values for same wall
        """,
        impact="""
            Unit shear calculations may be incorrect.
            Holdown forces may be wrong.
        """,
        mitigation=[
            "Trust dimension callouts over scaled measurement",
            "Flag discrepancy for review",
            "Use schedule value if available",
            "Apply conservative (shorter) length for capacity"
        ],
        confidence_penalty=0.1
    )
}
```

### 11.2.2 Schedule Correlation Failures

```python
SCHEDULE_FAILURE_MODES = {
    'FM-GE-010': FailureMode(
        failure_id='FM-GE-010',
        category=FailureCategory.GEOMETRY_EXTRACTION,
        severity=FailureSeverity.ERROR,
        description="Schedule-to-plan mismatch",
        detection_logic="""
            - Number of walls in schedule != walls on plan
            - Wall marks don't correlate
            - Schedule references non-existent walls
        """,
        impact="""
            Cannot verify wall properties from schedule.
            May miss walls or apply wrong properties.
        """,
        mitigation=[
            "Attempt fuzzy matching on wall location/length",
            "Flag unmatched entries",
            "Generate correlation report for review",
            "Allow manual mapping interface"
        ],
        confidence_penalty=0.25
    ),

    'FM-GE-011': FailureMode(
        failure_id='FM-GE-011',
        category=FailureCategory.GEOMETRY_EXTRACTION,
        severity=FailureSeverity.WARNING,
        description="Incomplete schedule data",
        detection_logic="""
            - Required columns missing (unit shear, nailing, sheathing)
            - Values missing for some walls
            - Notes reference 'TBD' or 'VERIFY'
        """,
        impact="""
            Cannot complete capacity calculations.
            Must make assumptions.
        """,
        mitigation=[
            "Apply code-minimum defaults",
            "Flag affected walls as 'ASSUMED'",
            "Cross-reference with typical details",
            "Request complete schedule from user"
        ],
        confidence_penalty=0.15
    )
}
```

---

## 11.3 Structural Analysis Failures

### 11.3.1 Load Path Failures

```python
STRUCTURAL_FAILURE_MODES = {
    'FM-SA-001': FailureMode(
        failure_id='FM-SA-001',
        category=FailureCategory.STRUCTURAL_ANALYSIS,
        severity=FailureSeverity.CRITICAL,
        description="Discontinuous load path",
        detection_logic="""
            - Shear wall at upper level has no supporting wall below
            - Gap in rod run path exceeds floor height
            - No holdown at transition point
        """,
        impact="""
            Structural load path incomplete.
            Design is structurally inadequate.
        """,
        mitigation=[
            "Flag as critical design issue",
            "Identify potential collector paths",
            "Search for alternative load paths",
            "STOP processing and require resolution",
            "Generate RFI for design team"
        ],
        confidence_penalty=0.5
    ),

    'FM-SA-002': FailureMode(
        failure_id='FM-SA-002',
        category=FailureCategory.STRUCTURAL_ANALYSIS,
        severity=FailureSeverity.ERROR,
        description="Rod capacity exceeded",
        detection_logic="""
            - Utilization ratio > 1.0 for any rod
            - Maximum available diameter (1.5") insufficient
            - Cumulative load exceeds all standard sizes
        """,
        impact="""
            Design cannot be completed with standard hardware.
            Alternative solutions required.
        """,
        mitigation=[
            "Try higher grade rod material",
            "Evaluate paired rod configuration",
            "Flag for collector/strut addition",
            "Recommend wall length increase",
            "Alert PE for alternative design"
        ],
        confidence_penalty=0.4
    ),

    'FM-SA-003': FailureMode(
        failure_id='FM-SA-003',
        category=FailureCategory.STRUCTURAL_ANALYSIS,
        severity=FailureSeverity.WARNING,
        description="High utilization ratio",
        detection_logic="""
            - Utilization ratio > 0.95
            - Limited capacity margin
            - Minor load increase would exceed capacity
        """,
        impact="""
            Design has minimal safety margin.
            Any additional loads may cause issues.
        """,
        mitigation=[
            "Recommend next size up for margin",
            "Document limited reserve capacity",
            "Flag for PE review",
            "Verify all loads accounted for"
        ],
        confidence_penalty=0.1
    ),

    'FM-SA-004': FailureMode(
        failure_id='FM-SA-004',
        category=FailureCategory.STRUCTURAL_ANALYSIS,
        severity=FailureSeverity.ERROR,
        description="Shrinkage exceeds take-up capacity",
        detection_logic="""
            - Calculated shrinkage > largest take-up device travel
            - Net movement after elongation > device capacity
            - Multiple take-up devices needed but not feasible
        """,
        impact="""
            Rod system will become loose over time.
            Lateral resistance compromised.
        """,
        mitigation=[
            "Specify multiple take-up devices per rod",
            "Recommend engineered lumber to reduce shrinkage",
            "Consider alternative shrinkage compensation",
            "Flag for special inspection requirements"
        ],
        confidence_penalty=0.3
    )
}
```

### 11.3.2 Calculation Verification Failures

```python
VERIFICATION_FAILURE_MODES = {
    'FM-SA-010': FailureMode(
        failure_id='FM-SA-010',
        category=FailureCategory.STRUCTURAL_ANALYSIS,
        severity=FailureSeverity.CRITICAL,
        description="Dual-pass verification failure",
        detection_logic="""
            - Primary and secondary calculation differ by > tolerance
            - Difference exceeds 5% for critical values
            - Cannot reconcile discrepancy
        """,
        impact="""
            Calculation reliability unknown.
            Cannot confirm design accuracy.
        """,
        mitigation=[
            "Run tertiary calculation with different method",
            "Identify source of discrepancy",
            "Apply conservative value",
            "Flag for manual verification",
            "Do not proceed without resolution"
        ],
        confidence_penalty=0.4
    ),

    'FM-SA-011': FailureMode(
        failure_id='FM-SA-011',
        category=FailureCategory.STRUCTURAL_ANALYSIS,
        severity=FailureSeverity.ERROR,
        description="Calculation engine exception",
        detection_logic="""
            - Division by zero encountered
            - Negative value where positive required
            - NaN or infinite result
            - Iteration did not converge
        """,
        impact="""
            Calculation incomplete.
            Affected rod run not designed.
        """,
        mitigation=[
            "Log input values for debugging",
            "Apply fallback calculation method",
            "Use conservative defaults",
            "Flag for manual calculation",
            "Report bug for investigation"
        ],
        confidence_penalty=0.3
    )
}
```

---

## 11.4 Code Compliance Failures

```python
CODE_FAILURE_MODES = {
    'FM-CC-001': FailureMode(
        failure_id='FM-CC-001',
        category=FailureCategory.CODE_COMPLIANCE,
        severity=FailureSeverity.ERROR,
        description="Aspect ratio violation",
        detection_logic="""
            - Shear wall height/length > 2:1 (3.5:1 with reduction)
            - No aspect ratio reduction applied
            - Wall too narrow for height
        """,
        impact="""
            Wall does not qualify as code-compliant shear wall.
            Alternative lateral system required.
        """,
        mitigation=[
            "Apply aspect ratio reduction factor",
            "Flag if ratio > 3.5:1 (not permitted)",
            "Recommend wall extension",
            "Consider portal frame alternative",
            "Require PE determination"
        ],
        confidence_penalty=0.25
    ),

    'FM-CC-002': FailureMode(
        failure_id='FM-CC-002',
        category=FailureCategory.CODE_COMPLIANCE,
        severity=FailureSeverity.ERROR,
        description="Anchor edge distance violation",
        detection_logic="""
            - Required edge distance > available distance
            - Anchor too close to foundation edge
            - Conflicts with rebar placement
        """,
        impact="""
            Anchor capacity reduced or anchor not installable.
            Foundation modification may be required.
        """,
        mitigation=[
            "Calculate reduced capacity for edge distance",
            "Check if reduced capacity sufficient",
            "Recommend anchor type change",
            "Flag for foundation coordination",
            "Consider relocated rod run"
        ],
        confidence_penalty=0.2
    ),

    'FM-CC-003': FailureMode(
        failure_id='FM-CC-003',
        category=FailureCategory.CODE_COMPLIANCE,
        severity=FailureSeverity.WARNING,
        description="Special inspection requirements",
        detection_logic="""
            - High seismic demand triggers SI
            - Non-standard connection details
            - Epoxy anchor in seismic application
        """,
        impact="""
            Project requires special inspections.
            Cost and schedule implications.
        """,
        mitigation=[
            "Document SI requirements in report",
            "Include in construction notes",
            "Coordinate with inspection agency",
            "No design mitigation needed"
        ],
        confidence_penalty=0.05
    )
}
```

---

## 11.5 Coordination Failures

```python
COORDINATION_FAILURE_MODES = {
    'FM-CO-001': FailureMode(
        failure_id='FM-CO-001',
        category=FailureCategory.COORDINATION,
        severity=FailureSeverity.CRITICAL,
        description="Critical MEP clash",
        detection_logic="""
            - Rod intersects HVAC main duct
            - Rod conflicts with fire sprinkler main
            - No feasible rod relocation available
        """,
        impact="""
            Rod cannot be installed as designed.
            Requires coordination meeting.
        """,
        mitigation=[
            "Evaluate alternative rod routing",
            "Check if MEP can be relocated",
            "Generate clash report for coordination",
            "Escalate to project team",
            "Consider wall relocation"
        ],
        confidence_penalty=0.35
    ),

    'FM-CO-002': FailureMode(
        failure_id='FM-CO-002',
        category=FailureCategory.COORDINATION,
        severity=FailureSeverity.ERROR,
        description="Incomplete MEP information",
        detection_logic="""
            - MEP drawings not provided
            - MEP model outdated
            - Significant MEP areas undefined
        """,
        impact="""
            Clash detection incomplete.
            Field conflicts likely.
        """,
        mitigation=[
            "Note incomplete clash detection in report",
            "Request current MEP drawings",
            "Flag all rod runs as 'VERIFY IN FIELD'",
            "Recommend coordination meeting",
            "Apply conservative clearances"
        ],
        confidence_penalty=0.2
    ),

    'FM-CO-003': FailureMode(
        failure_id='FM-CO-003',
        category=FailureCategory.COORDINATION,
        severity=FailureSeverity.WARNING,
        description="Drawing revision mismatch",
        detection_logic="""
            - Structural and MEP drawing dates differ significantly
            - Referenced revisions don't match
            - Conflicting geometry between disciplines
        """,
        impact="""
            Analysis may be based on outdated information.
            Coordination issues possible.
        """,
        mitigation=[
            "Document drawing dates/revisions used",
            "Request current coordinated set",
            "Flag affected areas",
            "Include revision tracking in report"
        ],
        confidence_penalty=0.15
    )
}
```

---

## 11.6 Failure Detection Engine

```python
from typing import List, Set
import logging

class FailureDetectionEngine:
    """Detect and track failure modes during processing."""

    def __init__(self):
        self.detected_failures: List[Dict] = []
        self.critical_failures: Set[str] = set()
        self.confidence_penalties: List[float] = []
        self.logger = logging.getLogger(__name__)

    def check_scale_detection(self, drawing_data: Dict) -> Optional[Dict]:
        """Check for scale detection failures."""
        failure_mode = FAILURE_MODES['FM-DI-001']

        # Check for scale presence
        if not drawing_data.get('scale_factor'):
            return self._create_failure_record(
                failure_mode,
                context={'drawing_id': drawing_data.get('drawing_id')},
                details="No scale factor detected"
            )

        # Check for scale reasonableness
        scale = drawing_data['scale_factor']
        if scale < 0.01 or scale > 10:  # Unrealistic scale
            return self._create_failure_record(
                failure_mode,
                context={'scale_factor': scale},
                details=f"Unrealistic scale factor: {scale}"
            )

        return None

    def check_shear_wall_identification(
        self,
        wall_data: Dict,
        schedule_data: Dict
    ) -> Optional[Dict]:
        """Check for ambiguous shear wall identification."""
        failure_mode = FAILURE_MODES['FM-GE-001']

        # Check for sheathing specification
        if not wall_data.get('sheathing_type'):
            if not wall_data.get('schedule_match'):
                return self._create_failure_record(
                    failure_mode,
                    context={'wall_id': wall_data.get('wall_id')},
                    details="No sheathing type and no schedule correlation"
                )

        # Check for holdown presence
        if not wall_data.get('holdowns'):
            failure_mode = FAILURE_MODES['FM-GE-002']
            return self._create_failure_record(
                failure_mode,
                context={'wall_id': wall_data.get('wall_id')},
                details="No holdowns detected at shear wall ends"
            )

        return None

    def check_load_path_continuity(
        self,
        rod_run: Dict,
        wall_stack: List[Dict]
    ) -> Optional[Dict]:
        """Check for load path discontinuity."""
        failure_mode = STRUCTURAL_FAILURE_MODES['FM-SA-001']

        for i in range(len(wall_stack) - 1):
            upper = wall_stack[i]
            lower = wall_stack[i + 1]

            # Check vertical alignment
            offset = abs(upper.get('center_x', 0) - lower.get('center_x', 0))
            if offset > 12:  # More than 12 inches offset
                return self._create_failure_record(
                    failure_mode,
                    context={
                        'rod_run_id': rod_run.get('rod_run_id'),
                        'upper_level': upper.get('level'),
                        'lower_level': lower.get('level'),
                        'offset_inches': offset
                    },
                    details=f"Wall stack offset of {offset:.1f}\" exceeds 12\" tolerance"
                )

        return None

    def check_dual_pass_verification(
        self,
        primary_result: float,
        secondary_result: float,
        tolerance: float = 0.02
    ) -> Optional[Dict]:
        """Check for verification failure."""
        failure_mode = VERIFICATION_FAILURE_MODES['FM-SA-010']

        if primary_result == 0:
            return None

        difference = abs(primary_result - secondary_result) / primary_result

        if difference > tolerance:
            return self._create_failure_record(
                failure_mode,
                context={
                    'primary_value': primary_result,
                    'secondary_value': secondary_result,
                    'difference_percent': difference * 100
                },
                details=f"Verification difference of {difference*100:.2f}% exceeds {tolerance*100}% tolerance"
            )

        return None

    def _create_failure_record(
        self,
        failure_mode: FailureMode,
        context: Dict,
        details: str
    ) -> Dict:
        """Create a failure record."""
        record = {
            'failure_id': failure_mode.failure_id,
            'category': failure_mode.category.value,
            'severity': failure_mode.severity.value,
            'description': failure_mode.description,
            'details': details,
            'context': context,
            'mitigation': failure_mode.mitigation,
            'confidence_penalty': failure_mode.confidence_penalty,
            'timestamp': datetime.utcnow().isoformat()
        }

        self.detected_failures.append(record)
        self.confidence_penalties.append(failure_mode.confidence_penalty)

        if failure_mode.severity in [FailureSeverity.CRITICAL, FailureSeverity.FATAL]:
            self.critical_failures.add(failure_mode.failure_id)

        self.logger.warning(
            f"Failure detected: {failure_mode.failure_id} - {details}"
        )

        return record

    def get_confidence_impact(self) -> float:
        """Calculate total confidence impact from failures."""
        if not self.confidence_penalties:
            return 1.0

        # Multiplicative penalty (allows stacking)
        total_impact = 1.0
        for penalty in self.confidence_penalties:
            total_impact *= (1.0 - penalty)

        return max(0.1, total_impact)  # Floor at 10%

    def can_proceed(self) -> bool:
        """Check if processing can continue."""
        return len(self.critical_failures) == 0

    def get_failure_summary(self) -> Dict:
        """Generate failure summary report."""
        by_category = {}
        by_severity = {}

        for failure in self.detected_failures:
            cat = failure['category']
            sev = failure['severity']

            by_category[cat] = by_category.get(cat, 0) + 1
            by_severity[sev] = by_severity.get(sev, 0) + 1

        return {
            'total_failures': len(self.detected_failures),
            'critical_count': len(self.critical_failures),
            'by_category': by_category,
            'by_severity': by_severity,
            'confidence_impact': self.get_confidence_impact(),
            'can_proceed': self.can_proceed(),
            'failures': self.detected_failures
        }
```

---

## 11.7 Recovery and Fallback Procedures

```python
class RecoveryManager:
    """Manage failure recovery and fallback procedures."""

    def __init__(self, failure_engine: FailureDetectionEngine):
        self.failure_engine = failure_engine
        self.recovery_log: List[Dict] = []

    def attempt_recovery(self, failure_record: Dict) -> Dict:
        """Attempt to recover from a failure."""
        failure_id = failure_record['failure_id']

        recovery_handlers = {
            'FM-DI-001': self._recover_scale_detection,
            'FM-GE-001': self._recover_ambiguous_wall,
            'FM-GE-002': self._recover_missing_holdown,
            'FM-SA-001': self._recover_discontinuous_load_path,
            'FM-SA-002': self._recover_capacity_exceeded,
        }

        handler = recovery_handlers.get(failure_id)
        if handler:
            result = handler(failure_record)
            self.recovery_log.append({
                'failure_id': failure_id,
                'recovery_attempted': True,
                'result': result,
                'timestamp': datetime.utcnow().isoformat()
            })
            return result

        return {
            'success': False,
            'message': 'No recovery handler available',
            'requires_manual': True
        }

    def _recover_scale_detection(self, failure_record: Dict) -> Dict:
        """Attempt to recover from scale detection failure."""
        context = failure_record.get('context', {})

        # Try to find known dimension reference
        recovery_methods = [
            self._find_door_dimension,
            self._find_dimension_callout,
            self._compare_grid_spacing,
        ]

        for method in recovery_methods:
            result = method(context)
            if result.get('success'):
                return result

        return {
            'success': False,
            'message': 'Scale could not be determined automatically',
            'requires_manual': True,
            'suggested_action': 'User must provide scale factor'
        }

    def _recover_missing_holdown(self, failure_record: Dict) -> Dict:
        """Recover from missing holdown."""
        context = failure_record.get('context', {})
        wall_id = context.get('wall_id')

        # Place default holdown at wall ends
        return {
            'success': True,
            'message': 'Default holdown placed at wall ends',
            'action_taken': 'HOLDOWN_DEFAULTED',
            'assumption_logged': True,
            'requires_verification': True,
            'data': {
                'wall_id': wall_id,
                'holdown_model': 'HDU14',  # Conservative default
                'placement': 'WALL_ENDS',
                'flagged': True
            }
        }

    def _recover_capacity_exceeded(self, failure_record: Dict) -> Dict:
        """Recover from rod capacity exceeded."""
        context = failure_record.get('context', {})

        # Try higher grade material
        alternatives = [
            {'grade': 'A325', 'fy_ksi': 92},
            {'grade': 'A449', 'fy_ksi': 58},
            {'grade': 'A354-BD', 'fy_ksi': 130}
        ]

        for alt in alternatives:
            # Recalculate with higher grade
            new_capacity = self._calculate_capacity_with_grade(
                context.get('diameter'),
                alt['fy_ksi']
            )
            if new_capacity > context.get('demand', float('inf')):
                return {
                    'success': True,
                    'message': f"Higher grade material ({alt['grade']}) provides adequate capacity",
                    'action_taken': 'MATERIAL_UPGRADED',
                    'data': {
                        'original_grade': 'A307',
                        'new_grade': alt['grade'],
                        'new_capacity': new_capacity
                    }
                }

        return {
            'success': False,
            'message': 'No standard rod configuration provides adequate capacity',
            'requires_manual': True,
            'suggested_action': 'Consider paired rods or alternative system'
        }
```
