# Section 12 — Hard Constraints

## 12.1 System Boundary Conditions

### 12.1.1 Building Configuration Constraints

```python
HARD_CONSTRAINTS = {
    "building": {
        "stories": {
            "min": 3,
            "max": 7,
            "validation": "3 <= stories <= 7",
            "rationale": "System designed for mid-rise Type V wood frame"
        },
        "construction_type": {
            "allowed": ["TYPE_V_A", "TYPE_V_B"],
            "default": "TYPE_V_A",
            "rationale": "Type V wood frame construction per CBC Chapter 6"
        },
        "height_limit_ft": {
            "TYPE_V_A": 60,
            "TYPE_V_B": 40,
            "source": "CBC Table 504.3"
        }
    },

    "seismic": {
        "design_category": {
            "allowed": ["D", "D0", "D1", "D2", "E", "F"],
            "minimum": "D",
            "rationale": "System designed for high seismic regions"
        },
        "overstrength_factor": {
            "omega_0": 3.0,
            "source": "ASCE 7-22 Table 12.2-1",
            "system": "Light-frame wood walls with shear panels"
        },
        "redundancy_factor": {
            "rho_values": [1.0, 1.3],
            "default": 1.0,
            "source": "ASCE 7-22 §12.3.4"
        },
        "response_modification": {
            "R": 6.5,
            "source": "ASCE 7-22 Table 12.2-1"
        }
    },

    "materials": {
        "rod_diameters_in": {
            "allowed": [0.625, 0.750, 0.875, 1.000, 1.125, 1.250, 1.375, 1.500],
            "min": 0.625,
            "max": 1.500
        },
        "rod_grades": {
            "allowed": ["ASTM_A307", "ASTM_A36", "ASTM_A193_B7", "ASTM_A449"],
            "default": "ASTM_A307",
            "minimum_fu_ksi": 60
        },
        "wood_species": {
            "allowed": ["DF_L", "SPF", "SYP", "HEM_FIR"],
            "default": "DF_L"
        }
    },

    "hardware": {
        "manufacturers": {
            "primary": ["SIMPSON", "MITEK"],
            "secondary": ["USP", "SENCO"]
        }
    },

    "code_references": {
        "building_code": ["CBC 2022", "CBC 2019", "IBC 2021", "IBC 2024"],
        "seismic_code": ["ASCE 7-22", "ASCE 7-16"],
        "wood_code": ["NDS 2024", "NDS 2018"],
        "shear_wall_standard": ["SDPWS 2021", "SDPWS 2015"],
        "steel_code": ["AISC 360-22", "AISC 360-16"],
        "concrete_code": ["ACI 318-19", "ACI 318-14"]
    }
}
```

---

## 12.2 Governing Equations Reference

| Equation | Formula | Code Reference |
|----------|---------|----------------|
| Seismic Base Shear | V = Cs × W | ASCE 7-22 §12.8.1 |
| Response Coefficient | Cs = SDS / (R/Ie) | ASCE 7-22 §12.8.1.1 |
| Vertical Distribution | Fx = Cvx × V | ASCE 7-22 §12.8.3 |
| Overturning Moment | Mx = Σ Fi × (hi - hx) | ASCE 7-22 §12.8.5 |
| Holdown Tension | T = (Mot/d) - 0.6D | SDPWS §4.3.6.1 |
| Cumulative Tension | T_total(n) = Σ T_level(i) | - |
| Rod Capacity (ASD) | Ta = (0.75×Fu×As)/Ω | AISC 360-22 §J3.6 |
| Rod Capacity (LRFD) | φTn = φ×0.75×Fu×As | AISC 360-22 §J3.6 |
| Tensile Stress Area | As = (π/4)(d - 0.9743/n)² | ASME B1.1 |
| Wood Shrinkage | Δ = t × S × ΔMC | Wood Handbook |
| Rod Elongation | Δ_rod = (T×L)/(As×E) | - |
| Anchor Breakout | Nb = kc×λa×√f'c×hef^1.5 | ACI 318-19 §17.6.2.2 |
| Bearing Stress | fb = P/A ≤ Fc_perp×CD×CM×Ct×Cb | NDS 2024 §3.10 |
| Aspect Ratio | AR = h/bs ≤ 3.5 | SDPWS §4.3.4 |

---

## 12.3 Tolerance Thresholds

### 12.3.1 Audit Tolerance Values

```python
AUDIT_TOLERANCES = {
    "forces": {
        "tension_percent": 2.0,
        "tension_absolute_lb": 500,
        "shear_percent": 2.0,
        "moment_percent": 2.0,
        "moment_absolute_ft_lb": 1000
    },
    "geometry": {
        "length_percent": 1.0,
        "length_absolute_in": 0.5,
        "position_absolute_in": 0.25,
        "elevation_absolute_ft": 0.1
    },
    "materials": {
        "shrinkage_percent": 5.0,
        "shrinkage_absolute_in": 0.1,
        "elongation_percent": 5.0,
        "elongation_absolute_in": 0.05
    },
    "design": {
        "utilization_absolute": 0.02,
        "capacity_percent": 1.0
    },
    "anchorage": {
        "embed_depth_percent": 5.0,
        "embed_depth_absolute_in": 0.5,
        "bearing_stress_percent": 2.0
    }
}
```

---

## 12.4 Quality Gates

| Gate | Description | Criteria | Failure Action |
|------|-------------|----------|----------------|
| 1 | Input Validation | All inputs within ranges | HALT |
| 2 | Geometry Extraction | Wall confidence > 70% | FLAG |
| 3 | Design Completion | All utilizations ≤ 1.0 | REDESIGN |
| 4 | Verification Pass | No critical discrepancies | REVIEW |
| 5 | PE Approval | All comments resolved | REVISE |

---

## 12.5 Material Properties

### Rod Material Properties

| Grade | Fy (ksi) | Fu (ksi) |
|-------|----------|----------|
| ASTM A307 | 36 | 60 |
| ASTM A36 | 36 | 58 |
| ASTM A193-B7 | 105 | 125 |
| ASTM A449 | 92 | 120 |

### Wood Shrinkage Coefficients

| Species | Coefficient |
|---------|-------------|
| DF-L | 0.00267 |
| SPF | 0.00236 |
| SYP | 0.00262 |
| Hem-Fir | 0.00249 |

---

## 12.6 Validation Rules

```python
from pydantic import BaseModel, Field, validator

class ProjectInputValidation(BaseModel):
    stories: int = Field(..., ge=3, le=7)
    construction_type: str
    seismic_design_category: str
    sds: float = Field(..., gt=0, le=3.0)
    sd1: float = Field(..., gt=0, le=2.0)

    @validator('construction_type')
    def validate_construction_type(cls, v):
        allowed = ["TYPE_V_A", "TYPE_V_B"]
        if v not in allowed:
            raise ValueError(f"Must be one of {allowed}")
        return v

    @validator('seismic_design_category')
    def validate_sdc(cls, v):
        allowed = ["D", "D0", "D1", "D2", "E", "F"]
        if v not in allowed:
            raise ValueError(f"Must be one of {allowed}")
        return v

class RodRunValidation(BaseModel):
    rod_diameter_in: float
    rod_grade: str
    total_length_ft: float = Field(..., gt=0, le=100)
    demand_tension_lb: float = Field(..., ge=0)

    @validator('rod_diameter_in')
    def validate_diameter(cls, v):
        allowed = [0.625, 0.750, 0.875, 1.000, 1.125, 1.250, 1.375, 1.500]
        if v not in allowed:
            raise ValueError(f"Must be one of {allowed}")
        return v
```
