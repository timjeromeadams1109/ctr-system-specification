# Autonomous Multi-Agent Continuous Threaded Rod Engineering System

## Implementation-Grade Technical Specification v2.0

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

A fully autonomous, multi-agent engineering system for designing continuous threaded rod (CTR) systems in multi-family wood-frame construction.

---

## Overview

This specification defines a complete system capable of:

- **Parsing multi-family construction drawing sets** (DWG, DXF, PDF, IFC)
- **Designing continuous threaded rod systems** per ASCE 7, NDS, SDPWS, and ACI 318
- **Performing self-verification loops** with dual-pass calculation architecture
- **Running internal structural audits** with tolerance-based discrepancy detection
- **Generating clash detection** using 3D spatial indexing (R-tree)
- **Tracking revisions** across drawing updates with persistent entity IDs
- **Producing PE-review-ready outputs** with digital signature workflow
- **Assigning confidence scores** based on weighted multi-factor analysis
- **Maintaining legal defensibility** through immutable audit trails

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      CHIEF ORCHESTRATOR AGENT                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │  Drawing    │  │  Geometry   │  │ Shear Wall  │  │  Load Path  │   │
│  │  Ingestion  │──│ Normalize   │──│  Detection  │──│   Analysis  │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
│         │                                                   │          │
│         ▼                                                   ▼          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │    Rod      │  │  Shrinkage  │  │    Clash    │  │    Code     │   │
│  │   Design    │──│  Analysis   │──│  Detection  │──│  Compliance │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
│         │                                                   │          │
│         ▼                                                   ▼          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │ Structural  │  │  Revision   │  │ Confidence  │  │   Report    │   │
│  │   Audit     │──│    Diff     │──│   Scoring   │──│ Generation  │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
│                                                             │          │
│                                                             ▼          │
│                                                    ┌─────────────┐     │
│                                                    │  PE Review  │     │
│                                                    │  Interface  │     │
│                                                    └─────────────┘     │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Documentation Structure

### Section 1 — Agent Architecture
**[01-agent-architecture.md](docs/01-agent-architecture.md)**

Defines all 14 specialized agents in the system:
- **Chief Orchestrator Agent** — Pipeline coordination, agent lifecycle, state management
- **Drawing Ingestion Agent** — DWG/DXF/PDF parsing, OCR, scale detection
- **Geometry Normalization Agent** — Coordinate systems, grid alignment, unit conversion
- **Shear Wall Detection Agent** — Wall identification, schedule correlation, holdown extraction
- **Load Path Analysis Agent** — Vertical continuity, stack validation, force distribution
- **Rod Design Agent** — Sizing, cumulative tension, hardware selection
- **Shrinkage Analysis Agent** — Wood movement, take-up device specification
- **Clash Detection Agent** — 3D spatial indexing, MEP coordination
- **Code Compliance Agent** — CBC/IBC/ASCE 7 verification
- **Structural Audit Agent** — Independent recalculation, dual-pass verification
- **Revision Diff Agent** — Drawing comparison, change tracking
- **Confidence Scoring Agent** — Risk assessment, PE review recommendations
- **Report Generation Agent** — PDF/CSV/DXF output production
- **PE Review Interface Agent** — Digital signature workflow, stamp management

### Section 2 — Engineering Core
**[02-engineering-core.md](docs/02-engineering-core.md)**

Complete structural engineering formulas and algorithms:
- Overturning moment calculations
- Tension demand with dead load offset
- Cumulative axial force through multiple levels
- ASD and LRFD load combinations per ASCE 7-22
- Wood shrinkage computation per NDS
- Rod elongation under service loads
- Utilization ratio calculations
- Seismic base shear distribution
- Foundation anchorage design per ACI 318

### Section 3 — Verification Loop
**[03-verification-loop.md](docs/03-verification-loop.md)**

Dual-pass self-verification architecture:
- Primary calculation by Rod Design Agent
- Secondary verification by Structural Audit Agent
- Tolerance thresholds for all parameters
- Discrepancy detection and resolution
- Automatic flagging and PE escalation
- Hash-based calculation integrity

### Section 4 — Confidence Scoring
**[04-confidence-scoring.md](docs/04-confidence-scoring.md)**

Weighted multi-factor confidence model:
- Component weight definitions
- Scoring formulas with penalty factors
- Project factor adjustments
- Risk classification thresholds (LOW/MODERATE/HIGH/CRITICAL)
- PE review intensity recommendations
- Score breakdown visualization

### Section 5 — Clash Detection
**[05-clash-detection.md](docs/05-clash-detection.md)**

3D geometric intersection engine:
- Axis-Aligned Bounding Box (AABB) mathematics
- Oriented Bounding Box (OBB) representation
- Parametric cylinder intersection algorithms
- Cylinder-cylinder clash detection
- Cylinder-box intersection for beams/headers
- R-tree spatial indexing with rtree/libspatialindex
- Clearance requirements by element type
- Severity classification and resolution recommendations

### Section 6 — Revision Differencing
**[06-revision-differencing.md](docs/06-revision-differencing.md)**

Drawing revision comparison system:
- Entity correlation engine with persistent IDs
- Geometry-based fuzzy matching
- Attribute-based matching
- Property differencing with change classification
- Structural and cost impact assessment
- Material quantity delta calculation
- Hash-based ID persistence across revisions

### Section 7 — Liability and PE Workflow
**[07-liability-workflow.md](docs/07-liability-workflow.md)**

Legal defensibility and professional engineering:
- Standard engineering disclaimer templates
- Assumption logging system with categories and sources
- Immutable audit trail with hash chain integrity
- PE stamp workflow with digital signatures
- Review comment tracking and resolution
- Document signature verification
- Multi-stage approval process

### Section 8 — Enterprise Implementation
**[08-enterprise-implementation.md](docs/08-enterprise-implementation.md)**

Production deployment architecture:
- Technology stack recommendations (Python 3.11+, FastAPI, PostgreSQL)
- Microservices architecture diagram
- API contract definitions with Pydantic models
- FastAPI endpoint specifications
- Role-based authentication and authorization
- Multi-tenant project isolation
- PostgreSQL/PostGIS database schema
- Index optimization strategies

### Section 9 — Scalability and Performance
**[09-scalability.md](docs/09-scalability.md)**

Enterprise scaling strategies:
- Per-project compute load projections
- Agent-specific resource profiles
- Memory budget allocation and management
- LRU drawing cache implementation
- Horizontal scaling with worker pools
- Auto-scaling policies by metric type
- Database partitioning strategies
- Multi-tier caching architecture
- Performance benchmarks and targets
- Disaster recovery procedures

### Section 10 — Output Formats
**[10-output-formats.md](docs/10-output-formats.md)**

Deliverable specifications:
- Engineering report PDF structure with section definitions
- PDF generation engine implementation
- Rod schedule CSV column specifications
- Rod schedule JSON schema with full hierarchy
- DXF overlay layer naming conventions
- DXF generation with ezdxf
- Block definitions for symbols
- IFC export for BIM integration
- Revit family parameter mappings

### Section 11 — Failure Modes
**[11-failure-modes.md](docs/11-failure-modes.md)**

Comprehensive failure handling:
- Drawing interpretation failures (scale, title block, grid detection)
- Layer interpretation and classification failures
- Shear wall detection ambiguities
- Schedule correlation mismatches
- Load path discontinuity detection
- Structural analysis failures (capacity, shrinkage, verification)
- Code compliance violations
- MEP coordination failures
- Failure detection engine implementation
- Recovery and fallback procedures

### Section 12 — Hard Constraints
**[12-hard-constraints.md](docs/12-hard-constraints.md)**

System boundaries and validation:
- Building configuration limits (3-7 stories)
- Material specifications and allowable grades
- Governing code references
- Tolerance threshold tables
- Input validation rules
- Non-negotiable safety requirements

---

## Example Implementations

Working code examples demonstrating core system functionality:

| Example | Description |
|---------|-------------|
| [basic_rod_design.py](src/examples/basic_rod_design.py) | Rod sizing calculations, tension demand, capacity checks |
| [shrinkage_analysis.py](src/examples/shrinkage_analysis.py) | Wood shrinkage, rod elongation, take-up device selection |
| [clash_detection.py](src/examples/clash_detection.py) | 3D spatial indexing, cylinder/box intersections |
| [confidence_scoring.py](src/examples/confidence_scoring.py) | Weighted scoring model, risk classification |
| [full_project_workflow.py](src/examples/full_project_workflow.py) | Complete pipeline from drawings to report |

### Running Examples

```bash
# Basic rod design
python src/examples/basic_rod_design.py

# Shrinkage analysis
python src/examples/shrinkage_analysis.py

# Clash detection
python src/examples/clash_detection.py

# Confidence scoring
python src/examples/confidence_scoring.py

# Full workflow demonstration
python src/examples/full_project_workflow.py
```

### Example Output

```
>>> Running basic_rod_design.py

ROD RUN DESIGN RESULTS: RR-A-01
======================================================================
Selected Rod: 0.875" diameter, A307
Total Length: 47.5 ft
Maximum Tension: 28,450 lb
Allowable Tension: 31,875 lb
Utilization Ratio: 0.89

Level   Level Tension (lb)     Cumulative (lb)     Status
----------------------------------------------------------------------
5              4,200               4,200             OK
4              5,100               9,300             OK
3              5,800              15,100             OK
2              6,350              21,450             OK
1              7,000              28,450             OK
```

---

## Hard Constraints

### Building Configuration
- **Stories:** 3-7 (Type V wood-frame construction)
- **Construction Type:** TYPE_V_A or TYPE_V_B per CBC
- **Seismic Design Category:** D or higher (California Building Code)

### Materials
- **Rod Diameters:** 5/8" to 1-1/2" (standard sizes)
- **Rod Grades:** ASTM A307, A36, A193-B7, A449
- **Hardware:** Simpson Strong-Tie ATS/ATUD or MiTek Hardy equivalent

### Code References
- ASCE 7-22 (Seismic and Wind)
- NDS 2024 (Wood Design)
- SDPWS 2021 (Shear Walls)
- ACI 318-19 (Concrete Anchorage)
- AISC 360-22 (Steel Components)

---

## Governing Equations

### Overturning Moment
```
M_OT = V × h
```

### Tension Demand
```
T = (M_OT / d) - 0.6D   (ASD)
T = (M_OT / d) - 0.9D   (LRFD)
```

### Cumulative Rod Tension
```
T_total(n) = Σ T_level(i)  for i = n to roof
```

### Wood Shrinkage
```
Δ_shrinkage = t × S × ΔMC
```

### Rod Elongation
```
Δ_rod = (T × L) / (A_s × E)
```

### Rod Capacity (ASD)
```
T_allowable = (0.75 × F_u × A_s) / Ω
```

---

## Technology Stack

### Backend
- **Language:** Python 3.11+
- **Framework:** FastAPI
- **Task Queue:** Celery + Redis

### Geometry Engine
- **CAD Parsing:** ezdxf, PyMuPDF, ifcopenshell
- **Computation:** Shapely, Open3D, NumPy
- **Spatial Index:** rtree (libspatialindex)

### Database
- **Relational:** PostgreSQL 15+ with PostGIS
- **Document:** MongoDB
- **Cache:** Redis

### Cloud Infrastructure
- **Compute:** AWS ECS/EKS
- **Storage:** S3, RDS
- **Security:** AWS KMS, WAF

---

## Quick Start

```bash
# Clone repository
git clone https://github.com/timjeromeadams1109/ctr-system-specification.git
cd ctr-system-specification

# Install dependencies
pip install -r requirements.txt

# Run example
python src/examples/basic_design.py
```

---

## API Example

```python
from ctr_system import CTRDesignEngine

# Initialize engine
engine = CTRDesignEngine(
    load_basis="ASD",
    code_year=2022,
    rod_manufacturer="SIMPSON"
)

# Load project
project = engine.create_project(
    name="Sample 5-Story",
    stories=5,
    seismic_design_category="D",
    sds=1.2,
    sd1=0.6
)

# Process drawings
project.upload_drawings("path/to/drawings/")
project.process()

# Get results
rod_schedule = project.get_rod_schedule()
confidence = project.get_confidence_score()

print(f"Confidence Score: {confidence}/100")
print(f"Total Rod Runs: {len(rod_schedule)}")
```

---

## Confidence Scoring

The system computes an overall confidence score (0-100) based on:

| Component | Weight |
|-----------|--------|
| Drawing Ingestion | 15% |
| Geometry Normalization | 10% |
| Shear Wall Detection | 20% |
| Load Path Analysis | 15% |
| Rod Design | 20% |
| Clash Detection | 5% |
| Code Compliance | 10% |
| Structural Audit | 15% |

### Risk Classification
- **85-100:** LOW risk - Standard PE review
- **70-84:** MODERATE risk - Enhanced review
- **50-69:** HIGH risk - Detailed review
- **0-49:** CRITICAL risk - Full recalculation recommended

---

## Self-Verification System

The system implements mandatory dual-pass verification:

1. **Pass 1:** Primary rod design by Rod Design Agent
2. **Pass 2:** Independent recalculation by Structural Audit Agent

### Tolerance Thresholds
| Parameter | Tolerance |
|-----------|-----------|
| Tension Force | 2% or 500 lb |
| Geometry | 0.5" |
| Shrinkage | 0.1" |
| Utilization | 0.02 |

---

## Output Formats

- **Engineering Report:** PDF with PE stamp area
- **Rod Schedule:** CSV + JSON
- **Hardware Schedule:** CSV
- **Overlay Instructions:** DXF with standardized layers
- **Clash Report:** PDF + JSON
- **Audit Log:** JSON with hash chain

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## Contact

For questions or support, please open an issue on GitHub.
