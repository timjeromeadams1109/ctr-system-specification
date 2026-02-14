# Section 10 — Output Formats

## 10.1 Engineering Report PDF Structure

### 10.1.1 Report Sections

```yaml
engineering_report_structure:
  cover_page:
    - project_name
    - project_address
    - report_date
    - revision_number
    - pe_stamp_area
    - firm_logo
    - confidentiality_notice

  table_of_contents:
    auto_generated: true
    include_figures: true
    include_tables: true

  executive_summary:
    - project_scope
    - design_basis_summary
    - key_findings
    - confidence_score
    - pe_review_recommendation

  section_1_introduction:
    - project_description
    - building_geometry
    - construction_type
    - applicable_codes
    - software_version

  section_2_design_criteria:
    - seismic_parameters
    - load_combinations
    - material_properties
    - hardware_specifications
    - safety_factors

  section_3_shear_wall_analysis:
    - wall_schedule_table
    - wall_location_plans
    - unit_shear_calculations
    - aspect_ratio_checks
    - holdown_requirements

  section_4_rod_system_design:
    - rod_run_schedule
    - load_accumulation_diagrams
    - rod_sizing_calculations
    - shrinkage_analysis
    - elongation_calculations
    - take_up_device_schedule

  section_5_foundation_anchorage:
    - anchor_schedule
    - embedment_calculations
    - edge_distance_checks
    - reinforcement_interference

  section_6_clash_detection:
    - clash_summary_table
    - clash_location_diagrams
    - resolution_recommendations
    - coordination_notes

  section_7_verification:
    - dual_pass_results
    - discrepancy_summary
    - tolerance_compliance
    - audit_findings

  appendices:
    appendix_a: "Detailed Calculations"
    appendix_b: "Drawing References"
    appendix_c: "Hardware Cut Sheets"
    appendix_d: "Assumptions Log"
    appendix_e: "Audit Trail Summary"
```

### 10.1.2 PDF Generation Engine

```python
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
import io

class PageSize(Enum):
    LETTER = (8.5, 11)
    LEGAL = (8.5, 14)
    TABLOID = (11, 17)
    ARCH_D = (24, 36)

@dataclass
class ReportStyle:
    """PDF report styling configuration."""
    page_size: PageSize = PageSize.LETTER
    margins_in: tuple = (1.0, 1.0, 1.0, 1.0)  # top, right, bottom, left
    header_font: str = "Helvetica-Bold"
    body_font: str = "Helvetica"
    code_font: str = "Courier"
    title_size: int = 24
    heading1_size: int = 16
    heading2_size: int = 14
    body_size: int = 10
    table_size: int = 9
    line_spacing: float = 1.15

@dataclass
class TableDefinition:
    """Table structure for PDF generation."""
    title: str
    columns: List[Dict[str, any]]  # name, width, align
    rows: List[List[any]]
    footer: Optional[str] = None
    notes: Optional[List[str]] = None

class EngineeringReportGenerator:
    """Generate PE-ready engineering report PDF."""

    def __init__(self, project_data: Dict, style: ReportStyle = None):
        self.project = project_data
        self.style = style or ReportStyle()
        self.page_number = 0
        self.toc_entries = []

    def generate(self) -> bytes:
        """Generate complete engineering report PDF."""
        buffer = io.BytesIO()

        # Create PDF document
        self._init_document(buffer)

        # Generate sections
        self._generate_cover_page()
        self._generate_toc_placeholder()
        self._generate_executive_summary()
        self._generate_design_criteria()
        self._generate_shear_wall_section()
        self._generate_rod_system_section()
        self._generate_anchorage_section()
        self._generate_clash_section()
        self._generate_verification_section()
        self._generate_appendices()

        # Update TOC
        self._update_toc()

        # Finalize
        self._finalize_document()

        buffer.seek(0)
        return buffer.read()

    def _generate_rod_system_section(self):
        """Generate rod system design section."""
        self._add_heading("Rod System Design", level=1)

        # Rod run schedule table
        rod_schedule = TableDefinition(
            title="Rod Run Schedule",
            columns=[
                {'name': 'Rod Run ID', 'width': 1.2, 'align': 'left'},
                {'name': 'Grid', 'width': 0.8, 'align': 'center'},
                {'name': 'Dir', 'width': 0.5, 'align': 'center'},
                {'name': 'Dia. (in)', 'width': 0.7, 'align': 'center'},
                {'name': 'Length (ft)', 'width': 0.8, 'align': 'right'},
                {'name': 'Max Tension (lb)', 'width': 1.0, 'align': 'right'},
                {'name': 'Capacity (lb)', 'width': 1.0, 'align': 'right'},
                {'name': 'Util.', 'width': 0.6, 'align': 'center'},
            ],
            rows=self._get_rod_schedule_rows(),
            notes=[
                "Rod material: ASTM A307 Grade A (Fy = 36 ksi)",
                "Capacity based on 0.75 × Tensile Stress Area × Fy",
                "Utilization ratio must not exceed 1.0"
            ]
        )
        self._add_table(rod_schedule)

        # Load accumulation diagram
        self._add_heading("Load Accumulation", level=2)
        for rod_run in self.project['rod_runs'][:3]:  # Sample first 3
            self._add_load_diagram(rod_run)

        # Shrinkage analysis
        self._add_heading("Shrinkage Analysis", level=2)
        self._add_shrinkage_summary()

    def _generate_verification_section(self):
        """Generate verification results section."""
        self._add_heading("Verification Results", level=1)

        # Dual-pass comparison
        self._add_heading("Dual-Pass Analysis", level=2)
        verification = self.project.get('verification', {})

        comparison_table = TableDefinition(
            title="Calculation Comparison Summary",
            columns=[
                {'name': 'Rod Run', 'width': 1.5, 'align': 'left'},
                {'name': 'Primary (lb)', 'width': 1.2, 'align': 'right'},
                {'name': 'Secondary (lb)', 'width': 1.2, 'align': 'right'},
                {'name': 'Difference', 'width': 1.0, 'align': 'right'},
                {'name': 'Status', 'width': 1.0, 'align': 'center'},
            ],
            rows=self._get_verification_rows(),
            footer=f"All calculations within {verification.get('tolerance', 2)}% tolerance"
        )
        self._add_table(comparison_table)

        # Confidence score breakdown
        self._add_heading("Confidence Score", level=2)
        self._add_confidence_breakdown()
```

---

## 10.2 Rod Schedule CSV Format

### 10.2.1 Column Specification

```csv
rod_run_id,project_id,direction,grid_location,position,start_level,end_level,rod_diameter_in,rod_grade,total_length_ft,segment_count,max_tension_lb,allowable_tension_lb,utilization_ratio,shrinkage_total_in,elongation_in,take_up_travel_in,foundation_anchor_type,anchor_embed_in,created_at,confidence_score
RR-A-01,proj-12345,NS,A,LEFT,1,5,0.875,A307,52.5,5,28450,31875,0.89,0.42,0.18,0.75,SSTB,12,2025-01-15T10:30:00Z,92
RR-A-02,proj-12345,NS,A,RIGHT,1,5,0.750,A307,52.5,5,22100,24750,0.89,0.42,0.15,0.75,SSTB,10,2025-01-15T10:30:00Z,94
RR-B-01,proj-12345,NS,B,LEFT,1,5,1.000,A307,52.5,5,38200,41600,0.92,0.42,0.21,1.00,SSTB,14,2025-01-15T10:30:00Z,88
```

### 10.2.2 CSV Schema Definition

```python
from dataclasses import dataclass
from typing import List
import csv
import io

@dataclass
class RodScheduleColumn:
    """Definition of a rod schedule CSV column."""
    name: str
    data_type: str
    description: str
    unit: str = ""
    required: bool = True

ROD_SCHEDULE_COLUMNS = [
    RodScheduleColumn("rod_run_id", "string", "Unique rod run identifier"),
    RodScheduleColumn("project_id", "string", "Project identifier"),
    RodScheduleColumn("direction", "enum", "NS or EW orientation"),
    RodScheduleColumn("grid_location", "string", "Grid line reference"),
    RodScheduleColumn("position", "enum", "LEFT, RIGHT, or CENTER"),
    RodScheduleColumn("start_level", "integer", "Starting floor level"),
    RodScheduleColumn("end_level", "integer", "Ending floor level"),
    RodScheduleColumn("rod_diameter_in", "decimal", "Rod diameter", "inches"),
    RodScheduleColumn("rod_grade", "string", "ASTM material grade"),
    RodScheduleColumn("total_length_ft", "decimal", "Total rod length", "feet"),
    RodScheduleColumn("segment_count", "integer", "Number of floor segments"),
    RodScheduleColumn("max_tension_lb", "decimal", "Maximum tension demand", "pounds"),
    RodScheduleColumn("allowable_tension_lb", "decimal", "Allowable tension capacity", "pounds"),
    RodScheduleColumn("utilization_ratio", "decimal", "Demand/capacity ratio"),
    RodScheduleColumn("shrinkage_total_in", "decimal", "Total wood shrinkage", "inches"),
    RodScheduleColumn("elongation_in", "decimal", "Rod elongation under load", "inches"),
    RodScheduleColumn("take_up_travel_in", "decimal", "Take-up device travel", "inches"),
    RodScheduleColumn("foundation_anchor_type", "string", "Anchor type at foundation"),
    RodScheduleColumn("anchor_embed_in", "decimal", "Anchor embedment depth", "inches"),
    RodScheduleColumn("created_at", "datetime", "Creation timestamp"),
    RodScheduleColumn("confidence_score", "decimal", "Confidence score 0-100"),
]

class RodScheduleExporter:
    """Export rod schedule to CSV format."""

    def __init__(self, rod_runs: List[Dict]):
        self.rod_runs = rod_runs

    def export_csv(self) -> str:
        """Export rod runs to CSV string."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Header row
        writer.writerow([col.name for col in ROD_SCHEDULE_COLUMNS])

        # Data rows
        for rod in self.rod_runs:
            row = [self._format_value(rod.get(col.name), col) for col in ROD_SCHEDULE_COLUMNS]
            writer.writerow(row)

        return output.getvalue()

    def _format_value(self, value, column: RodScheduleColumn) -> str:
        """Format value according to column type."""
        if value is None:
            return ""
        if column.data_type == "decimal":
            return f"{float(value):.3f}"
        if column.data_type == "integer":
            return str(int(value))
        return str(value)
```

---

## 10.3 Rod Schedule JSON Format

### 10.3.1 JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "RodScheduleExport",
  "type": "object",
  "properties": {
    "metadata": {
      "type": "object",
      "properties": {
        "project_id": {"type": "string"},
        "project_name": {"type": "string"},
        "export_timestamp": {"type": "string", "format": "date-time"},
        "software_version": {"type": "string"},
        "total_rod_runs": {"type": "integer"},
        "governing_code": {"type": "string"}
      },
      "required": ["project_id", "export_timestamp"]
    },
    "design_parameters": {
      "type": "object",
      "properties": {
        "seismic_design_category": {"type": "string"},
        "importance_factor": {"type": "number"},
        "overstrength_factor": {"type": "number"},
        "load_basis": {"enum": ["ASD", "LRFD"]},
        "rod_material_grade": {"type": "string"},
        "wood_species": {"type": "string"}
      }
    },
    "rod_runs": {
      "type": "array",
      "items": {"$ref": "#/$defs/RodRun"}
    },
    "summary": {
      "type": "object",
      "properties": {
        "total_rod_length_ft": {"type": "number"},
        "total_rod_weight_lb": {"type": "number"},
        "diameter_distribution": {
          "type": "object",
          "additionalProperties": {"type": "integer"}
        },
        "max_utilization_ratio": {"type": "number"},
        "average_confidence_score": {"type": "number"}
      }
    }
  },
  "$defs": {
    "RodRun": {
      "type": "object",
      "properties": {
        "rod_run_id": {"type": "string"},
        "direction": {"enum": ["NS", "EW"]},
        "grid_location": {"type": "string"},
        "position": {"enum": ["LEFT", "RIGHT", "CENTER"]},
        "geometry": {
          "type": "object",
          "properties": {
            "start_level": {"type": "integer"},
            "end_level": {"type": "integer"},
            "x_coordinate_ft": {"type": "number"},
            "y_coordinate_ft": {"type": "number"},
            "total_length_ft": {"type": "number"}
          }
        },
        "rod_properties": {
          "type": "object",
          "properties": {
            "diameter_in": {"type": "number"},
            "grade": {"type": "string"},
            "tensile_area_sq_in": {"type": "number"},
            "allowable_tension_lb": {"type": "number"}
          }
        },
        "load_analysis": {
          "type": "object",
          "properties": {
            "max_tension_demand_lb": {"type": "number"},
            "utilization_ratio": {"type": "number"},
            "governing_load_case": {"type": "string"},
            "level_tensions": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "level": {"type": "integer"},
                  "tension_lb": {"type": "number"},
                  "cumulative_lb": {"type": "number"}
                }
              }
            }
          }
        },
        "shrinkage_analysis": {
          "type": "object",
          "properties": {
            "total_shrinkage_in": {"type": "number"},
            "rod_elongation_in": {"type": "number"},
            "net_movement_in": {"type": "number"},
            "level_details": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "level": {"type": "integer"},
                  "plate_shrinkage_in": {"type": "number"},
                  "joist_shrinkage_in": {"type": "number"}
                }
              }
            }
          }
        },
        "hardware": {
          "type": "object",
          "properties": {
            "holdowns": {"type": "array", "items": {"$ref": "#/$defs/Holdown"}},
            "take_up_devices": {"type": "array", "items": {"$ref": "#/$defs/TakeUpDevice"}},
            "foundation_anchor": {"$ref": "#/$defs/FoundationAnchor"}
          }
        },
        "confidence_score": {"type": "number", "minimum": 0, "maximum": 100}
      },
      "required": ["rod_run_id", "direction", "grid_location"]
    },
    "Holdown": {
      "type": "object",
      "properties": {
        "level": {"type": "integer"},
        "model": {"type": "string"},
        "manufacturer": {"type": "string"},
        "allowable_tension_lb": {"type": "number"},
        "required_fasteners": {"type": "string"}
      }
    },
    "TakeUpDevice": {
      "type": "object",
      "properties": {
        "level": {"type": "integer"},
        "model": {"type": "string"},
        "travel_capacity_in": {"type": "number"},
        "required_travel_in": {"type": "number"}
      }
    },
    "FoundationAnchor": {
      "type": "object",
      "properties": {
        "type": {"type": "string"},
        "model": {"type": "string"},
        "diameter_in": {"type": "number"},
        "embedment_in": {"type": "number"},
        "edge_distance_in": {"type": "number"},
        "allowable_tension_lb": {"type": "number"}
      }
    }
  }
}
```

### 10.3.2 Sample JSON Output

```json
{
  "metadata": {
    "project_id": "proj-12345",
    "project_name": "Sunrise Apartments",
    "export_timestamp": "2025-01-15T10:30:00Z",
    "software_version": "1.0.0",
    "total_rod_runs": 24,
    "governing_code": "CBC 2022 / ASCE 7-22"
  },
  "design_parameters": {
    "seismic_design_category": "D",
    "importance_factor": 1.0,
    "overstrength_factor": 3.0,
    "load_basis": "ASD",
    "rod_material_grade": "ASTM A307 Grade A",
    "wood_species": "Douglas Fir-Larch"
  },
  "rod_runs": [
    {
      "rod_run_id": "RR-A-01",
      "direction": "NS",
      "grid_location": "A",
      "position": "LEFT",
      "geometry": {
        "start_level": 1,
        "end_level": 5,
        "x_coordinate_ft": 0.5,
        "y_coordinate_ft": 12.25,
        "total_length_ft": 52.5
      },
      "rod_properties": {
        "diameter_in": 0.875,
        "grade": "A307",
        "tensile_area_sq_in": 0.462,
        "allowable_tension_lb": 31875
      },
      "load_analysis": {
        "max_tension_demand_lb": 28450,
        "utilization_ratio": 0.89,
        "governing_load_case": "1.0D + 0.7E",
        "level_tensions": [
          {"level": 5, "tension_lb": 4200, "cumulative_lb": 4200},
          {"level": 4, "tension_lb": 5100, "cumulative_lb": 9300},
          {"level": 3, "tension_lb": 5800, "cumulative_lb": 15100},
          {"level": 2, "tension_lb": 6350, "cumulative_lb": 21450},
          {"level": 1, "tension_lb": 7000, "cumulative_lb": 28450}
        ]
      },
      "shrinkage_analysis": {
        "total_shrinkage_in": 0.42,
        "rod_elongation_in": 0.18,
        "net_movement_in": 0.24,
        "level_details": [
          {"level": 5, "plate_shrinkage_in": 0.021, "joist_shrinkage_in": 0.063},
          {"level": 4, "plate_shrinkage_in": 0.021, "joist_shrinkage_in": 0.063},
          {"level": 3, "plate_shrinkage_in": 0.021, "joist_shrinkage_in": 0.063},
          {"level": 2, "plate_shrinkage_in": 0.021, "joist_shrinkage_in": 0.063},
          {"level": 1, "plate_shrinkage_in": 0.021, "joist_shrinkage_in": 0.063}
        ]
      },
      "hardware": {
        "holdowns": [
          {"level": 5, "model": "HDU8", "manufacturer": "Simpson", "allowable_tension_lb": 14930},
          {"level": 4, "model": "HDU8", "manufacturer": "Simpson", "allowable_tension_lb": 14930},
          {"level": 3, "model": "HDU11", "manufacturer": "Simpson", "allowable_tension_lb": 18640},
          {"level": 2, "model": "HDU14", "manufacturer": "Simpson", "allowable_tension_lb": 23895},
          {"level": 1, "model": "HDU14", "manufacturer": "Simpson", "allowable_tension_lb": 23895}
        ],
        "take_up_devices": [
          {"level": 3, "model": "RTUD4", "travel_capacity_in": 1.0, "required_travel_in": 0.75}
        ],
        "foundation_anchor": {
          "type": "SSTB",
          "model": "SSTB16",
          "diameter_in": 0.875,
          "embedment_in": 12,
          "edge_distance_in": 4.5,
          "allowable_tension_lb": 35200
        }
      },
      "confidence_score": 92
    }
  ],
  "summary": {
    "total_rod_length_ft": 1260,
    "total_rod_weight_lb": 2570,
    "diameter_distribution": {
      "0.625": 4,
      "0.750": 8,
      "0.875": 8,
      "1.000": 4
    },
    "max_utilization_ratio": 0.94,
    "average_confidence_score": 89.5
  }
}
```

---

## 10.4 DXF Overlay Specification

### 10.4.1 Layer Naming Convention

```yaml
dxf_layers:
  rod_system:
    - name: "CTR-RODS-NS"
      color: 1  # Red
      description: "North-South rod runs"
      linetype: "CONTINUOUS"

    - name: "CTR-RODS-EW"
      color: 5  # Blue
      description: "East-West rod runs"
      linetype: "CONTINUOUS"

    - name: "CTR-HOLDOWNS"
      color: 3  # Green
      description: "Holdown locations"
      linetype: "CONTINUOUS"

    - name: "CTR-ANCHORS"
      color: 6  # Magenta
      description: "Foundation anchors"
      linetype: "CONTINUOUS"

    - name: "CTR-TAKEUP"
      color: 4  # Cyan
      description: "Take-up device locations"
      linetype: "CONTINUOUS"

    - name: "CTR-ANNOTATIONS"
      color: 7  # White/Black
      description: "Rod callouts and labels"
      linetype: "CONTINUOUS"

    - name: "CTR-CLASH"
      color: 1  # Red
      description: "Clash indicators"
      linetype: "DASHED"

  existing_reference:
    - name: "A-WALL-SHEAR"
      color: 8  # Gray
      description: "Shear wall outlines (reference)"
      linetype: "CONTINUOUS"
      plot: false
```

### 10.4.2 DXF Generation Engine

```python
import ezdxf
from ezdxf.enums import TextEntityAlignment
from typing import List, Dict, Tuple

class DXFOverlayGenerator:
    """Generate DXF overlay for CTR system."""

    def __init__(self, project_data: Dict, scale: float = 1/4):
        self.project = project_data
        self.scale = scale  # inches per drawing unit
        self.doc = ezdxf.new('R2018')
        self.msp = self.doc.modelspace()
        self._setup_layers()
        self._setup_blocks()

    def _setup_layers(self):
        """Create DXF layers."""
        layers = [
            ("CTR-RODS-NS", 1),
            ("CTR-RODS-EW", 5),
            ("CTR-HOLDOWNS", 3),
            ("CTR-ANCHORS", 6),
            ("CTR-TAKEUP", 4),
            ("CTR-ANNOTATIONS", 7),
            ("CTR-CLASH", 1),
        ]
        for name, color in layers:
            self.doc.layers.add(name, color=color)

    def _setup_blocks(self):
        """Create block definitions for symbols."""
        # Holdown symbol (square with X)
        hd_block = self.doc.blocks.new(name='HOLDOWN')
        size = 0.5 / self.scale
        hd_block.add_lwpolyline([
            (-size/2, -size/2), (size/2, -size/2),
            (size/2, size/2), (-size/2, size/2)
        ], close=True)
        hd_block.add_line((-size/2, -size/2), (size/2, size/2))
        hd_block.add_line((-size/2, size/2), (size/2, -size/2))

        # Anchor symbol (circle with +)
        anchor_block = self.doc.blocks.new(name='ANCHOR')
        radius = 0.375 / self.scale
        anchor_block.add_circle((0, 0), radius)
        anchor_block.add_line((-radius, 0), (radius, 0))
        anchor_block.add_line((0, -radius), (0, radius))

        # Take-up symbol (diamond)
        tu_block = self.doc.blocks.new(name='TAKEUP')
        size = 0.375 / self.scale
        tu_block.add_lwpolyline([
            (0, size), (size, 0), (0, -size), (-size, 0)
        ], close=True)

    def generate_floor_overlay(self, level: int) -> None:
        """Generate overlay for specific floor level."""
        rod_runs = [r for r in self.project['rod_runs']
                    if r['geometry']['start_level'] <= level <= r['geometry']['end_level']]

        for rod in rod_runs:
            self._draw_rod_location(rod, level)
            self._draw_holdown(rod, level)
            self._add_rod_callout(rod, level)

        # Add clashes for this level
        clashes = [c for c in self.project.get('clashes', [])
                   if c.get('level') == level]
        for clash in clashes:
            self._draw_clash_indicator(clash)

    def _draw_rod_location(self, rod: Dict, level: int):
        """Draw rod run location marker."""
        x = rod['geometry']['x_coordinate_ft'] * 12 / self.scale
        y = rod['geometry']['y_coordinate_ft'] * 12 / self.scale

        layer = f"CTR-RODS-{rod['direction']}"
        diameter = rod['rod_properties']['diameter_in']
        radius = (diameter / 2) / self.scale

        # Rod circle
        self.msp.add_circle((x, y), radius, dxfattribs={'layer': layer})

        # Direction indicator
        if rod['direction'] == 'NS':
            self.msp.add_line((x, y - radius * 2), (x, y + radius * 2),
                              dxfattribs={'layer': layer})
        else:
            self.msp.add_line((x - radius * 2, y), (x + radius * 2, y),
                              dxfattribs={'layer': layer})

    def _draw_holdown(self, rod: Dict, level: int):
        """Draw holdown symbol."""
        x = rod['geometry']['x_coordinate_ft'] * 12 / self.scale
        y = rod['geometry']['y_coordinate_ft'] * 12 / self.scale

        holdowns = rod['hardware'].get('holdowns', [])
        level_holdown = next((h for h in holdowns if h['level'] == level), None)

        if level_holdown:
            self.msp.add_blockref('HOLDOWN', (x, y),
                                  dxfattribs={'layer': 'CTR-HOLDOWNS'})

    def _add_rod_callout(self, rod: Dict, level: int):
        """Add rod identification callout."""
        x = rod['geometry']['x_coordinate_ft'] * 12 / self.scale
        y = rod['geometry']['y_coordinate_ft'] * 12 / self.scale

        offset = 1.0 / self.scale
        text_height = 0.125 / self.scale

        callout = f"{rod['rod_run_id']}\n{rod['rod_properties']['diameter_in']}\" DIA"

        self.msp.add_mtext(
            callout,
            dxfattribs={
                'layer': 'CTR-ANNOTATIONS',
                'char_height': text_height,
                'insert': (x + offset, y + offset)
            }
        )

    def _draw_clash_indicator(self, clash: Dict):
        """Draw clash warning indicator."""
        x = clash['location']['x'] * 12 / self.scale
        y = clash['location']['y'] * 12 / self.scale
        size = 0.5 / self.scale

        # Warning triangle
        points = [
            (x, y + size),
            (x - size * 0.866, y - size * 0.5),
            (x + size * 0.866, y - size * 0.5)
        ]
        self.msp.add_lwpolyline(points, close=True,
                                 dxfattribs={'layer': 'CTR-CLASH'})

        # Exclamation mark
        self.msp.add_text('!', dxfattribs={
            'layer': 'CTR-CLASH',
            'height': size * 0.6,
            'insert': (x - size * 0.1, y - size * 0.2)
        })

    def save(self, filepath: str):
        """Save DXF file."""
        self.doc.saveas(filepath)
```

### 10.4.3 DXF Export Options

```python
@dataclass
class DXFExportOptions:
    """Options for DXF overlay export."""
    scale: float = 0.25  # 1/4" = 1'-0"
    include_annotations: bool = True
    include_clashes: bool = True
    include_reference_walls: bool = False
    separate_files_per_level: bool = True
    coordinate_system: str = "project"  # or "drawing"
    units: str = "inches"
    version: str = "R2018"

class DXFExporter:
    """Export CTR system to DXF format."""

    def export(
        self,
        project_data: Dict,
        output_dir: str,
        options: DXFExportOptions = None
    ) -> List[str]:
        """Export DXF files for project."""
        options = options or DXFExportOptions()
        output_files = []

        if options.separate_files_per_level:
            levels = self._get_level_range(project_data)
            for level in levels:
                generator = DXFOverlayGenerator(project_data, options.scale)
                generator.generate_floor_overlay(level)
                filepath = f"{output_dir}/CTR_Level_{level}.dxf"
                generator.save(filepath)
                output_files.append(filepath)
        else:
            generator = DXFOverlayGenerator(project_data, options.scale)
            for level in self._get_level_range(project_data):
                generator.generate_floor_overlay(level)
            filepath = f"{output_dir}/CTR_All_Levels.dxf"
            generator.save(filepath)
            output_files.append(filepath)

        return output_files
```

---

## 10.5 BIM Integration Formats

### 10.5.1 IFC Export Schema

```python
class IFCExporter:
    """Export CTR system to IFC format for BIM integration."""

    def __init__(self, project_data: Dict):
        self.project = project_data

    def export_ifc(self, filepath: str):
        """Export to IFC 4.0 format."""
        import ifcopenshell
        import ifcopenshell.api

        model = ifcopenshell.api.run("project.create_file", version="IFC4")

        # Create project structure
        project = ifcopenshell.api.run("root.create_entity", model,
                                        ifc_class="IfcProject", name=self.project['name'])

        # Create site and building
        site = ifcopenshell.api.run("root.create_entity", model,
                                     ifc_class="IfcSite", name="Site")
        building = ifcopenshell.api.run("root.create_entity", model,
                                         ifc_class="IfcBuilding", name="Building")

        # Create building storeys
        for level in range(1, self.project['stories'] + 1):
            storey = ifcopenshell.api.run("root.create_entity", model,
                                           ifc_class="IfcBuildingStorey",
                                           name=f"Level {level}")

            # Add rod elements for this level
            self._add_level_rods(model, storey, level)

        model.write(filepath)

    def _add_level_rods(self, model, storey, level: int):
        """Add rod elements to IFC model."""
        import ifcopenshell.api

        for rod in self.project['rod_runs']:
            if rod['geometry']['start_level'] <= level <= rod['geometry']['end_level']:
                # Create mechanical fastener element
                element = ifcopenshell.api.run(
                    "root.create_entity", model,
                    ifc_class="IfcMechanicalFastener",
                    name=rod['rod_run_id']
                )

                # Add property set
                pset = ifcopenshell.api.run(
                    "pset.add_pset", model,
                    product=element,
                    name="Pset_CTRRodRun"
                )

                ifcopenshell.api.run(
                    "pset.edit_pset", model,
                    pset=pset,
                    properties={
                        "Diameter": rod['rod_properties']['diameter_in'],
                        "Grade": rod['rod_properties']['grade'],
                        "MaxTension": rod['load_analysis']['max_tension_demand_lb'],
                        "Utilization": rod['load_analysis']['utilization_ratio']
                    }
                )
```

### 10.5.2 Revit Family Parameters

```yaml
revit_family_parameters:
  ctr_rod_run:
    category: "Structural Connections"
    parameters:
      - name: "Rod_Run_ID"
        type: "Text"
        instance: true
      - name: "Rod_Diameter"
        type: "Length"
        instance: true
      - name: "Rod_Grade"
        type: "Text"
        instance: true
      - name: "Max_Tension"
        type: "Number"
        instance: true
        units: "pounds-force"
      - name: "Allowable_Tension"
        type: "Number"
        instance: true
        units: "pounds-force"
      - name: "Utilization_Ratio"
        type: "Number"
        instance: true
      - name: "Start_Level"
        type: "Integer"
        instance: true
      - name: "End_Level"
        type: "Integer"
        instance: true
      - name: "Total_Length"
        type: "Length"
        instance: true

  ctr_holdown:
    category: "Structural Connections"
    parameters:
      - name: "Holdown_Model"
        type: "Text"
        instance: true
      - name: "Manufacturer"
        type: "Text"
        instance: true
      - name: "Allowable_Load"
        type: "Number"
        instance: true
        units: "pounds-force"
      - name: "Associated_Rod_Run"
        type: "Text"
        instance: true
```
