# Section 8 — Enterprise Implementation Blueprint

## 8.1 Technology Stack Recommendations

### 8.1.1 Core Technology Stack

```yaml
backend:
  primary_language: Python 3.11+
  web_framework: FastAPI
  async_runtime: uvicorn + asyncio
  task_queue: Celery with Redis broker

geometry_engine:
  cad_parsing:
    dwg: ODA File Converter + ezdxf
    dxf: ezdxf
    pdf: PyMuPDF (fitz) + pdfplumber
    ifc: ifcopenshell
    rvt: Revit API or Forge API

  computational_geometry:
    primary: Shapely (2D), Open3D (3D)
    mesh_operations: trimesh
    spatial_indexing: rtree (libspatialindex)
    nurbs: geomdl

  visualization:
    2d: matplotlib, plotly
    3d: vtk, pyvista
    cad_output: ezdxf

math_engine:
  linear_algebra: NumPy, SciPy
  symbolic_math: SymPy
  units: pint
  optimization: scipy.optimize, cvxpy

database:
  primary: PostgreSQL 15+ with PostGIS
  document_store: MongoDB
  cache: Redis
  search: Elasticsearch

cloud_infrastructure:
  provider: AWS | GCP | Azure

  compute:
    api_servers: ECS Fargate / EKS
    workers: EC2 Spot Instances
    batch: AWS Batch

  storage:
    drawings: S3 with Intelligent Tiering
    database: RDS PostgreSQL Multi-AZ
    cache: ElastiCache Redis

  security:
    secrets: AWS Secrets Manager
    kms: AWS KMS
    waf: AWS WAF

gpu_requirements:
  optional: true
  use_cases:
    - Large PDF rasterization
    - ML-based element detection
    - Parallel clash detection
  recommended: NVIDIA T4 or better

parallelization:
  approach: Multi-process + async
  tools:
    - multiprocessing (CPU-bound)
    - asyncio (I/O-bound)
    - Dask (distributed computing)
```

---

## 8.2 Microservices Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY (Kong / AWS API Gateway)                 │
│                              Authentication + Rate Limiting                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
        ┌───────────────────────────────┼───────────────────────────────┐
        │                               │                               │
        ▼                               ▼                               ▼
┌───────────────┐               ┌───────────────┐               ┌───────────────┐
│   PROJECT     │               │   DRAWING     │               │    DESIGN     │
│   SERVICE     │               │   SERVICE     │               │   SERVICE     │
│               │               │               │               │               │
│ - Project CRUD│               │ - Upload/parse│               │ - Rod design  │
│ - Permissions │               │ - Geometry    │               │ - Load calc   │
│ - Workflow    │               │   extraction  │               │ - Shrinkage   │
└───────────────┘               └───────────────┘               └───────────────┘
        │                               │                               │
        └───────────────────────────────┼───────────────────────────────┘
                                        │
                                        ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                           MESSAGE QUEUE (Redis/RabbitMQ)                   │
└───────────────────────────────────────────────────────────────────────────┘
        │                               │                               │
        ▼                               ▼                               ▼
┌───────────────┐               ┌───────────────┐               ┌───────────────┐
│    CLASH      │               │    AUDIT      │               │   REPORT      │
│   SERVICE     │               │   SERVICE     │               │   SERVICE     │
└───────────────┘               └───────────────┘               └───────────────┘
        │                               │                               │
        └───────────────────────────────┼───────────────────────────────┘
                                        │
                                        ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                              DATA LAYER                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │ PostgreSQL  │  │  MongoDB    │  │   Redis     │  │    S3       │      │
│  │ (Relations) │  │ (Documents) │  │  (Cache)    │  │ (Files)     │      │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘      │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 8.3 API Contract Definitions

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

app = FastAPI(
    title="CTR Design System API",
    version="1.0.0",
    description="Continuous Threaded Rod Design Automation System"
)

# Data Models
class ProjectStatus(str, Enum):
    DRAFT = "DRAFT"
    PROCESSING = "PROCESSING"
    DESIGN_COMPLETE = "DESIGN_COMPLETE"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    address: str
    stories: int = Field(..., ge=3, le=7)
    construction_type: str = "TYPE_V_A"
    seismic_design_category: str = "D"

class ProjectResponse(BaseModel):
    project_id: str
    name: str
    status: ProjectStatus
    confidence_score: Optional[float]
    rod_run_count: Optional[int]

class RodRunResponse(BaseModel):
    rod_run_id: str
    direction: str
    grid_location: str
    diameter_in: float
    total_length_ft: float
    max_tension_lb: float
    utilization_ratio: float

# API Endpoints
@app.post("/api/v1/projects", response_model=ProjectResponse)
async def create_project(project: ProjectCreate):
    """Create a new CTR design project."""
    pass

@app.get("/api/v1/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    """Get project details."""
    pass

@app.post("/api/v1/projects/{project_id}/drawings")
async def upload_drawing(project_id: str):
    """Upload a drawing to the project."""
    pass

@app.post("/api/v1/projects/{project_id}/process")
async def start_processing(project_id: str):
    """Start automated processing pipeline."""
    pass

@app.get("/api/v1/projects/{project_id}/rod-runs", response_model=List[RodRunResponse])
async def get_rod_runs(project_id: str):
    """Get all designed rod runs."""
    pass

@app.post("/api/v1/projects/{project_id}/reports/engineering")
async def generate_engineering_report(project_id: str):
    """Generate PE-ready engineering report."""
    pass
```

---

## 8.4 Authentication and Authorization

```python
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    PROJECT_MANAGER = "PROJECT_MANAGER"
    ENGINEER = "ENGINEER"
    PE_REVIEWER = "PE_REVIEWER"
    VIEWER = "VIEWER"

class Permission(str, Enum):
    PROJECT_CREATE = "project:create"
    PROJECT_READ = "project:read"
    PROJECT_UPDATE = "project:update"
    DESIGN_RUN = "design:run"
    DESIGN_OVERRIDE = "design:override"
    REPORT_GENERATE = "report:generate"
    PE_REVIEW = "pe:review"
    PE_APPROVE = "pe:approve"

ROLE_PERMISSIONS = {
    UserRole.ADMIN: [Permission.PROJECT_CREATE, Permission.PROJECT_READ, ...],
    UserRole.PROJECT_MANAGER: [Permission.PROJECT_CREATE, Permission.PROJECT_READ, ...],
    UserRole.ENGINEER: [Permission.PROJECT_READ, Permission.DESIGN_RUN, ...],
    UserRole.PE_REVIEWER: [Permission.PROJECT_READ, Permission.PE_REVIEW, Permission.PE_APPROVE],
    UserRole.VIEWER: [Permission.PROJECT_READ]
}


class ProjectIsolation:
    """Multi-tenant project isolation."""

    @staticmethod
    def check_access(user, project) -> bool:
        # Same organization
        if user.organization_id == project.organization_id:
            return True

        # PE reviewer with explicit access
        if user.role == UserRole.PE_REVIEWER:
            if project.id in user.authorized_projects:
                return True

        return False
```

---

## 8.5 Database Schema

```sql
-- Core tables
CREATE TABLE projects (
    project_id UUID PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    organization_id UUID NOT NULL,
    status VARCHAR(50) NOT NULL,
    stories INTEGER CHECK (stories >= 3 AND stories <= 7),
    construction_type VARCHAR(20),
    seismic_design_category VARCHAR(5),
    confidence_score DECIMAL(5,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE rod_runs (
    rod_run_id VARCHAR(50) PRIMARY KEY,
    project_id UUID REFERENCES projects(project_id),
    direction VARCHAR(5),
    grid_location VARCHAR(20),
    position VARCHAR(10),
    rod_diameter_in DECIMAL(5,3),
    rod_grade VARCHAR(20),
    total_length_ft DECIMAL(6,2),
    max_tension_lb DECIMAL(10,2),
    utilization_ratio DECIMAL(4,3),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE shear_walls (
    wall_id VARCHAR(50) PRIMARY KEY,
    project_id UUID REFERENCES projects(project_id),
    level INTEGER,
    length_ft DECIMAL(6,2),
    orientation VARCHAR(10),
    sheathing_type VARCHAR(30),
    unit_shear_plf INTEGER,
    geometry GEOMETRY(LINESTRING)
);

-- Indexes
CREATE INDEX idx_rod_runs_project ON rod_runs(project_id);
CREATE INDEX idx_shear_walls_project ON shear_walls(project_id);
CREATE INDEX idx_shear_walls_geom ON shear_walls USING GIST(geometry);
```
