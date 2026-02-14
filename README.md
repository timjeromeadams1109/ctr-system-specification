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

| Document | Description |
|----------|-------------|
| [01-agent-architecture.md](docs/01-agent-architecture.md) | 14 specialized agents with I/O schemas |
| [02-engineering-core.md](docs/02-engineering-core.md) | Structural engineering formulas and algorithms |
| [03-verification-loop.md](docs/03-verification-loop.md) | Dual-pass verification system |
| [04-confidence-scoring.md](docs/04-confidence-scoring.md) | Weighted confidence scoring model |
| [05-clash-detection.md](docs/05-clash-detection.md) | 3D geometric intersection algorithms |
| [06-revision-differencing.md](docs/06-revision-differencing.md) | Entity correlation and diff engine |
| [07-liability-workflow.md](docs/07-liability-workflow.md) | PE stamp and audit trail system |
| [08-enterprise-implementation.md](docs/08-enterprise-implementation.md) | Technology stack and API contracts |
| [09-scalability.md](docs/09-scalability.md) | Performance projections and optimization |
| [10-output-formats.md](docs/10-output-formats.md) | Report, schedule, and overlay schemas |
| [11-failure-modes.md](docs/11-failure-modes.md) | Detection and mitigation strategies |
| [12-hard-constraints.md](docs/12-hard-constraints.md) | System boundaries and validation rules |

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
git clone https://github.com/yourusername/ctr-system-specification.git
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
