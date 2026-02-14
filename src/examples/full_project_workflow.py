"""
Full Project Workflow Example

Demonstrates the complete CTR design pipeline from drawing ingestion
through report generation.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from datetime import datetime
import json
import hashlib


# Import from other examples (in practice these would be proper imports)
# For this example, we'll include minimal implementations


class ProjectStatus(Enum):
    CREATED = "CREATED"
    DRAWINGS_UPLOADED = "DRAWINGS_UPLOADED"
    PROCESSING = "PROCESSING"
    DESIGN_COMPLETE = "DESIGN_COMPLETE"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    ARCHIVED = "ARCHIVED"


class LoadBasis(Enum):
    ASD = "ASD"
    LRFD = "LRFD"


@dataclass
class ProjectConfig:
    """Project configuration parameters."""
    name: str
    address: str
    stories: int
    construction_type: str = "TYPE_V_A"
    seismic_design_category: str = "D"
    sds: float = 1.2  # Short period spectral acceleration
    sd1: float = 0.6  # 1-second spectral acceleration
    load_basis: LoadBasis = LoadBasis.ASD
    rod_manufacturer: str = "SIMPSON"
    wood_species: str = "Douglas Fir-Larch"


@dataclass
class Drawing:
    """Uploaded drawing metadata."""
    drawing_id: str
    filename: str
    drawing_type: str  # STRUCTURAL, ARCHITECTURAL, MEP
    level: Optional[int]
    scale: Optional[float]
    upload_time: str
    status: str = "PENDING"


@dataclass
class ShearWall:
    """Detected shear wall entity."""
    wall_id: str
    level: int
    grid_location: str
    length_ft: float
    unit_shear_plf: int
    sheathing_type: str
    holdown_left: str
    holdown_right: str
    orientation: str  # NS or EW


@dataclass
class RodRun:
    """Designed rod run entity."""
    rod_run_id: str
    grid_location: str
    position: str  # LEFT, RIGHT, CENTER
    direction: str  # NS, EW
    start_level: int
    end_level: int
    rod_diameter_in: float
    rod_grade: str
    total_length_ft: float
    max_tension_lb: float
    allowable_tension_lb: float
    utilization_ratio: float
    shrinkage_in: float
    elongation_in: float
    take_up_device: str


@dataclass
class Clash:
    """Detected clash entity."""
    clash_id: str
    rod_run_id: str
    element_type: str
    element_id: str
    severity: str
    level: int
    description: str


@dataclass
class AuditEvent:
    """Audit trail event."""
    event_id: str
    timestamp: str
    event_type: str
    actor: str
    description: str
    data: Dict = field(default_factory=dict)


class CTRProject:
    """Main project orchestrator for CTR design."""

    def __init__(self, config: ProjectConfig):
        self.config = config
        self.project_id = self._generate_id()
        self.status = ProjectStatus.CREATED
        self.created_at = datetime.utcnow().isoformat() + "Z"

        # Data stores
        self.drawings: List[Drawing] = []
        self.shear_walls: List[ShearWall] = []
        self.rod_runs: List[RodRun] = []
        self.clashes: List[Clash] = []
        self.audit_trail: List[AuditEvent] = []

        # Scores
        self.component_scores: Dict[str, float] = {}
        self.confidence_score: Optional[float] = None

        self._log_event("PROJECT_CREATED", "System", f"Project '{config.name}' created")

    def _generate_id(self) -> str:
        """Generate unique project ID."""
        hash_input = f"{self.config.name}{datetime.utcnow().isoformat()}"
        return f"proj-{hashlib.md5(hash_input.encode()).hexdigest()[:12]}"

    def _log_event(self, event_type: str, actor: str, description: str, data: Dict = None):
        """Log an audit event."""
        event = AuditEvent(
            event_id=f"EVT-{len(self.audit_trail)+1:05d}",
            timestamp=datetime.utcnow().isoformat() + "Z",
            event_type=event_type,
            actor=actor,
            description=description,
            data=data or {}
        )
        self.audit_trail.append(event)

    def upload_drawing(self, filename: str, drawing_type: str, level: int = None) -> Drawing:
        """Upload a drawing to the project."""
        drawing = Drawing(
            drawing_id=f"DWG-{len(self.drawings)+1:03d}",
            filename=filename,
            drawing_type=drawing_type,
            level=level,
            scale=None,
            upload_time=datetime.utcnow().isoformat() + "Z"
        )
        self.drawings.append(drawing)
        self.status = ProjectStatus.DRAWINGS_UPLOADED

        self._log_event(
            "DRAWING_UPLOADED",
            "User",
            f"Drawing uploaded: {filename}",
            {"drawing_id": drawing.drawing_id, "type": drawing_type}
        )

        return drawing

    def process_drawings(self) -> Dict[str, int]:
        """
        Process all uploaded drawings.
        This simulates the full agent pipeline.
        """
        self.status = ProjectStatus.PROCESSING
        self._log_event("PROCESSING_STARTED", "System", "Automated processing initiated")

        results = {
            'drawings_processed': 0,
            'walls_detected': 0,
            'rod_runs_designed': 0,
            'clashes_detected': 0,
        }

        # Step 1: Drawing Ingestion
        print("\n[1/8] Drawing Ingestion Agent...")
        for drawing in self.drawings:
            drawing.scale = 0.25  # 1/4" = 1'-0"
            drawing.status = "PARSED"
            results['drawings_processed'] += 1
        self.component_scores['drawing_ingestion'] = 0.92
        self._log_event("DRAWINGS_PARSED", "System", f"Parsed {len(self.drawings)} drawings")

        # Step 2: Geometry Normalization
        print("[2/8] Geometry Normalization Agent...")
        self.component_scores['geometry_normalization'] = 0.95
        self._log_event("GEOMETRY_NORMALIZED", "System", "Coordinate system established")

        # Step 3: Shear Wall Detection
        print("[3/8] Shear Wall Detection Agent...")
        self._detect_shear_walls()
        results['walls_detected'] = len(self.shear_walls)
        self.component_scores['shear_wall_detection'] = 0.88
        self._log_event(
            "WALLS_DETECTED",
            "System",
            f"Detected {len(self.shear_walls)} shear walls"
        )

        # Step 4: Load Path Analysis
        print("[4/8] Load Path Analysis Agent...")
        self.component_scores['load_path_analysis'] = 0.90
        self._log_event("LOAD_PATH_ANALYZED", "System", "Load paths verified")

        # Step 5: Rod Design
        print("[5/8] Rod Design Agent...")
        self._design_rod_runs()
        results['rod_runs_designed'] = len(self.rod_runs)
        self.component_scores['rod_design'] = 0.94
        self._log_event(
            "RODS_DESIGNED",
            "System",
            f"Designed {len(self.rod_runs)} rod runs"
        )

        # Step 6: Shrinkage Analysis (integrated into rod design)
        print("[6/8] Shrinkage Analysis Agent...")
        self._log_event("SHRINKAGE_ANALYZED", "System", "Shrinkage calculations complete")

        # Step 7: Clash Detection
        print("[7/8] Clash Detection Agent...")
        self._detect_clashes()
        results['clashes_detected'] = len(self.clashes)
        self.component_scores['clash_detection'] = 0.85 if self.clashes else 1.0
        self._log_event(
            "CLASHES_DETECTED",
            "System",
            f"Found {len(self.clashes)} potential clashes"
        )

        # Step 8: Code Compliance
        print("[8/8] Code Compliance Agent...")
        self.component_scores['code_compliance'] = 0.98
        self._log_event("CODE_CHECKED", "System", "Code compliance verified")

        # Structural Audit (dual-pass verification)
        print("\n[AUDIT] Structural Audit Agent running verification...")
        self.component_scores['structural_audit'] = 0.92
        self._log_event("AUDIT_COMPLETE", "System", "Dual-pass verification complete")

        # Calculate confidence score
        print("\n[SCORE] Confidence Scoring Agent...")
        self._calculate_confidence_score()
        self._log_event(
            "CONFIDENCE_CALCULATED",
            "System",
            f"Confidence score: {self.confidence_score:.1f}/100"
        )

        self.status = ProjectStatus.DESIGN_COMPLETE
        self._log_event("PROCESSING_COMPLETE", "System", "All agents completed successfully")

        return results

    def _detect_shear_walls(self):
        """Simulate shear wall detection."""
        # Sample walls for a 5-story building
        grids = ['A', 'B', 'C', 'D']
        levels = range(1, self.config.stories + 1)

        wall_count = 0
        for grid in grids:
            for level in levels:
                # Varying unit shears by level (higher at bottom)
                base_shear = 300 + (self.config.stories - level) * 60
                length = 10.0 + (ord(grid) - ord('A')) * 2

                wall = ShearWall(
                    wall_id=f"SW-{grid}-L{level}",
                    level=level,
                    grid_location=grid,
                    length_ft=length,
                    unit_shear_plf=base_shear,
                    sheathing_type="15/32 OSB",
                    holdown_left=f"HDU{8 + level}",
                    holdown_right=f"HDU{8 + level}",
                    orientation="NS"
                )
                self.shear_walls.append(wall)
                wall_count += 1

        # Add some EW walls
        for level in levels:
            wall = ShearWall(
                wall_id=f"SW-1-L{level}",
                level=level,
                grid_location="1",
                length_ft=14.0,
                unit_shear_plf=280 + (self.config.stories - level) * 50,
                sheathing_type="15/32 OSB",
                holdown_left="HDU8",
                holdown_right="HDU8",
                orientation="EW"
            )
            self.shear_walls.append(wall)

    def _design_rod_runs(self):
        """Simulate rod run design."""
        # Group walls by grid for rod runs
        grids = set(w.grid_location for w in self.shear_walls if w.orientation == "NS")

        for grid in sorted(grids):
            grid_walls = [w for w in self.shear_walls
                         if w.grid_location == grid and w.orientation == "NS"]

            if not grid_walls:
                continue

            # Calculate cumulative tension (simplified)
            max_tension = sum(w.unit_shear_plf * w.length_ft * 0.8 for w in grid_walls)

            # Select rod size
            if max_tension < 15000:
                diameter = 0.625
            elif max_tension < 22000:
                diameter = 0.750
            elif max_tension < 30000:
                diameter = 0.875
            elif max_tension < 40000:
                diameter = 1.000
            else:
                diameter = 1.125

            # Calculate capacity
            capacity = diameter ** 2 * 0.785 * 0.75 * 60000 / 2  # Simplified

            rod = RodRun(
                rod_run_id=f"RR-{grid}-01",
                grid_location=grid,
                position="LEFT",
                direction="NS",
                start_level=1,
                end_level=self.config.stories,
                rod_diameter_in=diameter,
                rod_grade="A307",
                total_length_ft=self.config.stories * 9.5,
                max_tension_lb=max_tension,
                allowable_tension_lb=capacity,
                utilization_ratio=max_tension / capacity,
                shrinkage_in=self.config.stories * 0.08,
                elongation_in=max_tension * self.config.stories * 9.5 * 12 / (capacity * 29e6) * 1000,
                take_up_device="RTUD4"
            )
            self.rod_runs.append(rod)

            # Add right side rod
            rod_right = RodRun(
                rod_run_id=f"RR-{grid}-02",
                grid_location=grid,
                position="RIGHT",
                direction="NS",
                start_level=1,
                end_level=self.config.stories,
                rod_diameter_in=diameter,
                rod_grade="A307",
                total_length_ft=self.config.stories * 9.5,
                max_tension_lb=max_tension * 0.95,
                allowable_tension_lb=capacity,
                utilization_ratio=(max_tension * 0.95) / capacity,
                shrinkage_in=self.config.stories * 0.08,
                elongation_in=max_tension * 0.95 * self.config.stories * 9.5 * 12 / (capacity * 29e6) * 1000,
                take_up_device="RTUD4"
            )
            self.rod_runs.append(rod_right)

    def _detect_clashes(self):
        """Simulate clash detection."""
        # Add a couple of sample clashes
        self.clashes.append(Clash(
            clash_id="CLH-001",
            rod_run_id="RR-B-01",
            element_type="HVAC_DUCT",
            element_id="HVAC-301",
            severity="MINOR",
            level=3,
            description="Clearance 1.2\" vs 2.0\" required"
        ))
        self.clashes.append(Clash(
            clash_id="CLH-002",
            rod_run_id="RR-C-02",
            element_type="PLUMBING_PIPE",
            element_id="PLMB-401",
            severity="WARNING",
            level=4,
            description="Near clearance limit: 1.8\" (min 1.5\")"
        ))

    def _calculate_confidence_score(self):
        """Calculate overall confidence score."""
        weights = {
            'drawing_ingestion': 0.15,
            'geometry_normalization': 0.10,
            'shear_wall_detection': 0.20,
            'load_path_analysis': 0.15,
            'rod_design': 0.20,
            'clash_detection': 0.05,
            'code_compliance': 0.10,
            'structural_audit': 0.15,
        }

        total_weight = sum(weights.values())
        weighted_sum = sum(
            self.component_scores.get(comp, 0) * weight
            for comp, weight in weights.items()
        )

        self.confidence_score = (weighted_sum / total_weight) * 100

    def get_rod_schedule(self) -> List[Dict]:
        """Get rod schedule as list of dictionaries."""
        return [
            {
                'rod_run_id': r.rod_run_id,
                'grid_location': r.grid_location,
                'position': r.position,
                'direction': r.direction,
                'diameter_in': r.rod_diameter_in,
                'length_ft': r.total_length_ft,
                'max_tension_lb': r.max_tension_lb,
                'utilization': r.utilization_ratio,
                'take_up_device': r.take_up_device,
            }
            for r in self.rod_runs
        ]

    def generate_summary_report(self) -> str:
        """Generate text summary report."""
        lines = [
            "=" * 70,
            "CTR DESIGN SUMMARY REPORT",
            "=" * 70,
            "",
            f"Project: {self.config.name}",
            f"Address: {self.config.address}",
            f"Project ID: {self.project_id}",
            f"Generated: {datetime.utcnow().isoformat()}Z",
            "",
            "-" * 70,
            "BUILDING PARAMETERS",
            "-" * 70,
            f"Stories: {self.config.stories}",
            f"Construction Type: {self.config.construction_type}",
            f"Seismic Design Category: {self.config.seismic_design_category}",
            f"SDS: {self.config.sds}g",
            f"SD1: {self.config.sd1}g",
            f"Load Basis: {self.config.load_basis.value}",
            "",
            "-" * 70,
            "DESIGN SUMMARY",
            "-" * 70,
            f"Shear Walls Detected: {len(self.shear_walls)}",
            f"Rod Runs Designed: {len(self.rod_runs)}",
            f"Clashes Detected: {len(self.clashes)}",
            f"Confidence Score: {self.confidence_score:.1f}/100",
            "",
            "-" * 70,
            "ROD SCHEDULE",
            "-" * 70,
            f"{'Rod Run':<12}{'Grid':<8}{'Dia.':<8}{'Length':<10}{'Max T':<12}{'Util.':<8}",
            "-" * 70,
        ]

        for rod in self.rod_runs:
            lines.append(
                f"{rod.rod_run_id:<12}{rod.grid_location:<8}"
                f"{rod.rod_diameter_in}\"{'':4}{rod.total_length_ft:<10.1f}"
                f"{rod.max_tension_lb:<12,.0f}{rod.utilization_ratio:<8.2f}"
            )

        lines.extend([
            "",
            "-" * 70,
            "MATERIAL SUMMARY",
            "-" * 70,
        ])

        # Calculate totals by diameter
        by_diameter = {}
        for rod in self.rod_runs:
            d = rod.rod_diameter_in
            if d not in by_diameter:
                by_diameter[d] = {'count': 0, 'length': 0}
            by_diameter[d]['count'] += 1
            by_diameter[d]['length'] += rod.total_length_ft

        for d in sorted(by_diameter.keys()):
            info = by_diameter[d]
            lines.append(f"{d}\" Rod: {info['count']} runs, {info['length']:.1f} ft total")

        total_length = sum(r.total_length_ft for r in self.rod_runs)
        lines.append(f"\nTotal Rod Length: {total_length:.1f} ft")

        if self.clashes:
            lines.extend([
                "",
                "-" * 70,
                "CLASH SUMMARY",
                "-" * 70,
            ])
            for clash in self.clashes:
                lines.append(f"[{clash.severity}] {clash.rod_run_id} vs {clash.element_type}")
                lines.append(f"  Level {clash.level}: {clash.description}")

        lines.extend([
            "",
            "-" * 70,
            "CONFIDENCE SCORE BREAKDOWN",
            "-" * 70,
        ])

        for comp, score in sorted(self.component_scores.items()):
            lines.append(f"{comp.replace('_', ' ').title():<30} {score*100:.1f}")

        lines.append(f"\n{'OVERALL SCORE:':<30} {self.confidence_score:.1f}/100")

        # Risk classification
        if self.confidence_score >= 85:
            risk = "LOW"
            review = "Standard PE Review"
        elif self.confidence_score >= 70:
            risk = "MODERATE"
            review = "Enhanced PE Review"
        elif self.confidence_score >= 50:
            risk = "HIGH"
            review = "Detailed PE Review"
        else:
            risk = "CRITICAL"
            review = "Full Recalculation Recommended"

        lines.extend([
            f"Risk Classification: {risk}",
            f"PE Review: {review}",
            "",
            "=" * 70,
        ])

        return "\n".join(lines)

    def export_json(self) -> str:
        """Export project data as JSON."""
        data = {
            'project_id': self.project_id,
            'config': {
                'name': self.config.name,
                'address': self.config.address,
                'stories': self.config.stories,
                'construction_type': self.config.construction_type,
                'seismic_design_category': self.config.seismic_design_category,
                'sds': self.config.sds,
                'sd1': self.config.sd1,
                'load_basis': self.config.load_basis.value,
            },
            'status': self.status.value,
            'created_at': self.created_at,
            'confidence_score': self.confidence_score,
            'component_scores': self.component_scores,
            'statistics': {
                'drawings': len(self.drawings),
                'shear_walls': len(self.shear_walls),
                'rod_runs': len(self.rod_runs),
                'clashes': len(self.clashes),
            },
            'rod_runs': self.get_rod_schedule(),
            'clashes': [
                {
                    'clash_id': c.clash_id,
                    'rod_run_id': c.rod_run_id,
                    'element_type': c.element_type,
                    'severity': c.severity,
                    'level': c.level,
                    'description': c.description,
                }
                for c in self.clashes
            ],
            'audit_trail_count': len(self.audit_trail),
        }
        return json.dumps(data, indent=2)


# Example usage
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("CTR SYSTEM - FULL PROJECT WORKFLOW EXAMPLE")
    print("=" * 70)

    # Create project configuration
    config = ProjectConfig(
        name="Sunrise Apartments",
        address="123 Main Street, Los Angeles, CA 90001",
        stories=5,
        construction_type="TYPE_V_A",
        seismic_design_category="D",
        sds=1.2,
        sd1=0.6,
        load_basis=LoadBasis.ASD,
        rod_manufacturer="SIMPSON"
    )

    # Initialize project
    print("\n>>> Creating project...")
    project = CTRProject(config)
    print(f"Project ID: {project.project_id}")

    # Upload drawings
    print("\n>>> Uploading drawings...")
    drawings = [
        ("S1.1-Foundation-Plan.pdf", "STRUCTURAL", 1),
        ("S2.1-Level-2-Framing.pdf", "STRUCTURAL", 2),
        ("S2.2-Level-3-Framing.pdf", "STRUCTURAL", 3),
        ("S2.3-Level-4-Framing.pdf", "STRUCTURAL", 4),
        ("S2.4-Level-5-Framing.pdf", "STRUCTURAL", 5),
        ("S2.5-Roof-Framing.pdf", "STRUCTURAL", None),
        ("S3.1-Shear-Wall-Schedule.pdf", "STRUCTURAL", None),
        ("S4.1-Details.pdf", "STRUCTURAL", None),
        ("M1.1-Mechanical-Plan.pdf", "MEP", None),
        ("P1.1-Plumbing-Plan.pdf", "MEP", None),
    ]

    for filename, dtype, level in drawings:
        dwg = project.upload_drawing(filename, dtype, level)
        print(f"  Uploaded: {dwg.drawing_id} - {filename}")

    # Process drawings
    print("\n>>> Processing drawings (running agent pipeline)...")
    results = project.process_drawings()

    print("\n>>> Processing complete!")
    print(f"  Drawings processed: {results['drawings_processed']}")
    print(f"  Walls detected: {results['walls_detected']}")
    print(f"  Rod runs designed: {results['rod_runs_designed']}")
    print(f"  Clashes detected: {results['clashes_detected']}")

    # Generate report
    print("\n" + "=" * 70)
    print("GENERATING SUMMARY REPORT")
    print("=" * 70)
    report = project.generate_summary_report()
    print(report)

    # Export JSON
    print("\n>>> Exporting project data to JSON...")
    json_output = project.export_json()
    print("JSON export preview (first 1000 chars):")
    print(json_output[:1000] + "...")

    # Show audit trail
    print("\n" + "=" * 70)
    print("AUDIT TRAIL (Last 10 Events)")
    print("=" * 70)
    for event in project.audit_trail[-10:]:
        print(f"[{event.timestamp}] {event.event_type}: {event.description}")

    print("\n>>> Workflow complete!")
    print(f"Final Status: {project.status.value}")
    print(f"Confidence Score: {project.confidence_score:.1f}/100")
    print()
