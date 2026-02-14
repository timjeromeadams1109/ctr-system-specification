# Section 1 — Autonomous Multi-Agent Architecture

## 1.1 Agent Hierarchy and Specifications

### 1.1.1 Chief Orchestrator Agent (COA)

**Purpose:** Central coordinator managing workflow state, agent dispatch, dependency resolution, and global error handling.

**Inputs:**
```json
{
  "project_id": "string (UUID v4)",
  "drawing_set": {
    "files": ["array of file references"],
    "format": "enum: PDF | DWG | DXF | IFC | RVT",
    "page_manifest": [
      {
        "page_id": "string",
        "page_type": "enum: FOUNDATION | FLOOR_FRAMING | SHEAR_WALL_SCHEDULE | ELEVATION | SECTION | DETAIL",
        "scale": "string (e.g., '1/4\" = 1'-0\"')",
        "level": "integer (0 = foundation, 1 = first floor, etc.)"
      }
    ]
  },
  "project_metadata": {
    "address": "string",
    "stories": "integer (3-7)",
    "construction_type": "enum: TYPE_V_A | TYPE_V_B",
    "seismic_design_category": "enum: D | D0 | D1 | D2 | E",
    "wind_speed": "number (mph)",
    "exposure_category": "enum: B | C | D",
    "soil_class": "enum: A | B | C | D | E | F",
    "jurisdiction": "string",
    "code_year": "integer (2019 | 2022 | 2025)"
  },
  "design_preferences": {
    "rod_manufacturer": "enum: SIMPSON | MITEK | USP | GENERIC",
    "load_basis": "enum: ASD | LRFD",
    "shrinkage_device_preference": "enum: TAKE_UP | COUPLER | HYBRID",
    "min_rod_diameter": "number (inches, default 0.625)",
    "max_rod_diameter": "number (inches, default 1.5)"
  }
}
```

**Outputs:**
```json
{
  "orchestration_result": {
    "status": "enum: COMPLETED | FAILED | PARTIAL | PENDING_REVIEW",
    "execution_id": "string (UUID v4)",
    "timestamp_start": "ISO8601",
    "timestamp_end": "ISO8601",
    "agent_execution_log": [
      {
        "agent_id": "string",
        "agent_type": "string",
        "status": "enum: SUCCESS | FAILED | SKIPPED | RETRY",
        "attempts": "integer",
        "duration_ms": "integer",
        "error_messages": ["array of strings"],
        "output_reference": "string (pointer to output payload)"
      }
    ],
    "global_confidence_score": "number (0-100)",
    "deliverables": {
      "engineering_report": "file_reference",
      "rod_schedule": "file_reference",
      "clash_report": "file_reference",
      "overlay_instructions": "file_reference",
      "audit_log": "file_reference"
    },
    "pe_review_required": "boolean",
    "critical_flags": ["array of strings"]
  }
}
```

**Failure Modes:**
| Failure Mode | Detection Mechanism | Recovery Strategy |
|--------------|---------------------|-------------------|
| Agent timeout | Heartbeat monitoring (5s interval, 30s threshold) | Kill process, increment retry, dispatch to alternative worker |
| Circular dependency | DAG validation at dispatch | Reject workflow, report to user |
| Resource exhaustion | Memory/CPU threshold monitoring | Queue throttling, horizontal scale-out |
| Data corruption | Checksum validation on all inter-agent payloads | Rollback to last checkpoint, re-execute from checkpoint |
| External service failure | Health check endpoints | Circuit breaker pattern (5 failures = open, 60s reset) |

**Retry Logic:**
```python
RETRY_CONFIG = {
    "max_attempts": 3,
    "base_delay_ms": 1000,
    "max_delay_ms": 30000,
    "exponential_base": 2,
    "jitter_factor": 0.1,
    "retryable_errors": [
        "TIMEOUT",
        "RESOURCE_UNAVAILABLE",
        "TRANSIENT_GEOMETRY_ERROR",
        "EXTERNAL_SERVICE_UNAVAILABLE"
    ],
    "non_retryable_errors": [
        "INVALID_INPUT_SCHEMA",
        "MISSING_REQUIRED_DRAWING",
        "UNSUPPORTED_FORMAT",
        "LICENSE_VIOLATION"
    ]
}
```

**Confidence Contribution:**
- Base weight: 0.05 (orchestration quality)
- Factors: Agent completion rate, retry frequency, execution time variance

---

### 1.1.2 Drawing Ingestion Agent (DIA)

**Purpose:** Parse, validate, and extract raw geometric and textual data from construction documents.

**Inputs:**
```json
{
  "file_reference": {
    "uri": "string (s3:// | file:// | https://)",
    "format": "enum: PDF | DWG | DXF | IFC | RVT",
    "checksum_sha256": "string",
    "file_size_bytes": "integer"
  },
  "extraction_config": {
    "ocr_enabled": "boolean",
    "ocr_language": "string (default: 'eng')",
    "vector_extraction": "boolean",
    "raster_threshold_dpi": "integer (default: 300)",
    "layer_filter": ["array of layer names to include, empty = all"],
    "coordinate_system": "enum: WCS | UCS | PAGE"
  }
}
```

**Outputs:**
```json
{
  "ingestion_result": {
    "page_id": "string",
    "extraction_timestamp": "ISO8601",
    "raw_geometry": {
      "lines": [...],
      "polylines": [...],
      "arcs": [...],
      "circles": [...],
      "blocks": [...]
    },
    "text_entities": [...],
    "dimensions": [...],
    "detected_scale": {
      "scale_string": "string",
      "scale_factor": "number",
      "confidence": "number (0-1)",
      "detection_method": "enum: TITLE_BLOCK | DIMENSION_INFERENCE | KNOWN_ELEMENT | MANUAL"
    },
    "title_block_data": {...},
    "quality_metrics": {
      "extraction_completeness": "number (0-1)",
      "ocr_confidence_average": "number (0-1)",
      "geometry_density": "number (entities per sq inch)",
      "layer_count": "integer",
      "block_reference_count": "integer"
    }
  }
}
```

**Confidence Contribution:**
- Weight: 0.15
- Formula: `0.4 * extraction_completeness + 0.3 * ocr_confidence_avg + 0.2 * scale_confidence + 0.1 * (1 - error_rate)`

---

### 1.1.3 Geometry Normalization Agent (GNA)

**Purpose:** Transform raw geometry into normalized engineering coordinate system with consistent units, orientation, and spatial indexing.

**Confidence Contribution:**
- Weight: 0.10
- Formula: `0.5 * scale_confidence + 0.3 * level_mapping_accuracy + 0.2 * grid_alignment_score`

---

### 1.1.4 Shear Wall Detection Agent (SWDA)

**Purpose:** Identify, classify, and extract geometric and structural properties of shear wall lines from normalized geometry.

**Confidence Contribution:**
- Weight: 0.20
- Formula: `0.3 * detection_rate + 0.3 * schedule_match_rate + 0.2 * holdown_detection_rate + 0.2 * (1 - flag_count / wall_count)`

---

### 1.1.5 Load Path Agent (LPA)

**Purpose:** Trace vertical load paths through the structure, identify stacking relationships, and compute tributary loads for continuous rod design.

**Confidence Contribution:**
- Weight: 0.15
- Formula: `0.4 * stack_continuity_avg + 0.3 * force_equilibrium_accuracy + 0.3 * coverage_completeness`

---

### 1.1.6 Rod Design Agent (RDA)

**Purpose:** Design continuous threaded rod systems including diameter selection, coupler placement, take-up device specification, and hardware scheduling.

**Confidence Contribution:**
- Weight: 0.20
- Formula: `0.35 * (1 - max_utilization_ratio) + 0.25 * shrinkage_adequacy_score + 0.20 * hardware_completeness + 0.20 * force_calculation_confidence`

---

### 1.1.7 Shrinkage Analysis Agent (SAA)

**Purpose:** Calculate wood shrinkage accumulation through multi-story assemblies and verify adequacy of take-up device capacity.

---

### 1.1.8 Clash Detection Agent (CDA)

**Purpose:** Identify geometric interferences between rod runs and other building elements including MEP, structural framing, and architectural components.

**Confidence Contribution:**
- Weight: 0.05
- Formula: `1.0 - (critical_clash_count * 0.2 + major_clash_count * 0.1 + minor_clash_count * 0.02)`

---

### 1.1.9 Code Compliance Agent (CCA)

**Purpose:** Verify all design elements comply with applicable building codes (CBC/IBC), material standards (NDS, AISC), and seismic provisions (ASCE 7).

**Confidence Contribution:**
- Weight: 0.10
- Formula: `(pass_count / total_checks) * 0.7 + (1 - critical_failure_count * 0.15) * 0.3`

---

### 1.1.10 Structural Audit Agent (SAuA)

**Purpose:** Perform independent verification of all structural calculations as second-pass quality assurance.

**Confidence Contribution:**
- Weight: 0.15
- Formula: `0.5 * (verified_runs / total_runs) + 0.3 * (1 - max_discrepancy / tolerance) + 0.2 * checks_passed_ratio`

---

### 1.1.11 Revision Diff Agent (RevDA)

**Purpose:** Compare drawing revisions, identify changes affecting rod design, and track design evolution.

**Confidence Contribution:**
- Weight: 0.02
- Formula: `1.0 - (unresolved_conflict_count * 0.1)`

---

### 1.1.12 Confidence Scoring Agent (CSA)

**Purpose:** Aggregate confidence metrics from all agents and compute overall project confidence score.

---

### 1.1.13 Report Generation Agent (RGA)

**Purpose:** Generate all output documents including engineering reports, schedules, overlays, and audit logs.

**Confidence Contribution:**
- Weight: 0.03
- Formula: `generation_success_rate * (1 - error_count * 0.1)`

---

### 1.1.14 PE Review Interface Agent (PRIA)

**Purpose:** Present design results to PE reviewer with interactive review tools and approval workflow.

**Confidence Contribution:**
- Weight: 0.05
- Formula: `approval_rate * 0.8 + (1 - rejection_rate) * 0.2`

---

## 1.2 Message Schema Definitions

See [schemas/](../schemas/) directory for complete JSON schema definitions:

- `DrawingEntity.schema.json`
- `ShearWallEntity.schema.json`
- `HoldownEntity.schema.json`
- `RodRunEntity.schema.json`
- `ClashEntity.schema.json`
- `FoundationAnchorEntity.schema.json`
- `LoadCaseEntity.schema.json`
- `RevisionDeltaEntity.schema.json`
- `ComplianceCheckResult.schema.json`
