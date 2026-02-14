# Section 4 — Confidence Scoring Model

## 4.1 Scoring Framework

### 4.1.1 Weighted Component Model

The confidence scoring system aggregates metrics from all pipeline agents using a weighted contribution model:

$$\text{Overall Score} = \sum_{i=1}^{n} w_i \times s_i \times p_i$$

Where:
- $w_i$ = Base weight for component $i$
- $s_i$ = Component score (0-1)
- $p_i$ = Penalty factor for component $i$ (0-1, based on issues)

### 4.1.2 Component Weights

| Component | Base Weight | Description |
|-----------|-------------|-------------|
| Drawing Ingestion | 0.15 | Quality of drawing extraction |
| Geometry Normalization | 0.10 | Coordinate system accuracy |
| Shear Wall Detection | 0.20 | Wall identification accuracy |
| Load Path Analysis | 0.15 | Load path continuity |
| Rod Design | 0.20 | Design calculation confidence |
| Clash Detection | 0.05 | Interference identification |
| Code Compliance | 0.10 | Code check pass rate |
| Structural Audit | 0.15 | Verification agreement |
| Revision Tracking | 0.02 | Change tracking completeness |

**Note:** Weights sum to 1.12 to allow for bonus scoring when all components perform well.

---

## 4.2 Score Calculation Engine

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum

class RiskClassification(Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class PEReviewIntensity(Enum):
    STANDARD = "STANDARD"
    ENHANCED = "ENHANCED"
    DETAILED = "DETAILED"
    FULL_RECALC = "FULL_RECALC"

@dataclass
class ComponentScore:
    """Score contribution from a single component."""
    component_name: str
    base_weight: float
    raw_score: float  # 0-1
    penalty_factor: float = 1.0
    flags: List[str] = field(default_factory=list)

    @property
    def weighted_contribution(self) -> float:
        return self.base_weight * self.raw_score * self.penalty_factor

    @property
    def effective_score(self) -> float:
        return self.raw_score * self.penalty_factor


@dataclass
class ProjectFactors:
    """Project-level factors affecting confidence."""
    drawing_clarity: float  # 0-1
    schedule_completeness: float  # 0-1
    load_path_continuity: float  # 0-1
    conflict_density: float  # clashes per rod run
    code_compliance_certainty: float  # 0-1
    ambiguity_count: int
    assumption_count: int
    manual_override_count: int


class ConfidenceScoreEngine:
    """Calculate overall project confidence score."""

    COMPONENT_WEIGHTS = {
        'drawing_ingestion': 0.15,
        'geometry_normalization': 0.10,
        'shear_wall_detection': 0.20,
        'load_path_analysis': 0.15,
        'rod_design': 0.20,
        'clash_detection': 0.05,
        'code_compliance': 0.10,
        'structural_audit': 0.15,
        'revision_tracking': 0.02
    }

    def calculate_overall_score(self) -> float:
        """Calculate overall confidence score (0-100)."""
        if not self.component_scores:
            return 0.0

        raw_total = sum(
            cs.weighted_contribution
            for cs in self.component_scores.values()
        )

        total_weight = sum(
            cs.base_weight
            for cs in self.component_scores.values()
        )

        normalized_score = raw_total / total_weight if total_weight > 0 else 0

        # Apply project factor adjustments
        if self.project_factors:
            factor_adjustment = self._calculate_factor_adjustment()
            normalized_score *= factor_adjustment

        return min(100, max(0, normalized_score * 100))

    def _calculate_factor_adjustment(self) -> float:
        """Calculate adjustment from project factors."""
        pf = self.project_factors

        # Positive factors (boost score)
        positive = (
            0.1 * pf.drawing_clarity +
            0.1 * pf.schedule_completeness +
            0.15 * pf.load_path_continuity +
            0.1 * pf.code_compliance_certainty
        )

        # Negative factors (reduce score)
        conflict_penalty = min(0.2, pf.conflict_density * 0.05)
        ambiguity_penalty = min(0.15, pf.ambiguity_count * 0.01)
        assumption_penalty = min(0.15, pf.assumption_count * 0.01)
        override_penalty = min(0.1, pf.manual_override_count * 0.02)

        negative = conflict_penalty + ambiguity_penalty + assumption_penalty + override_penalty

        return max(0.5, min(1.2, 1.0 + positive - negative))
```

---

## 4.3 Scoring Formulas

### 4.3.1 Overall Confidence Score

$$C_{overall} = \min\left(100, \frac{\sum_{i=1}^{n} w_i \cdot s_i \cdot p_i}{\sum_{i=1}^{n} w_i} \times A_{project} \times 100\right)$$

### 4.3.2 Project Adjustment Factor

$$A_{project} = 1 + (F_{positive} - F_{negative})$$

$$F_{positive} = 0.1 \cdot C_{drawing} + 0.1 \cdot C_{schedule} + 0.15 \cdot C_{loadpath} + 0.1 \cdot C_{code}$$

$$F_{negative} = \min(0.2, 0.05 \cdot D_{clash}) + \min(0.15, 0.01 \cdot N_{ambig}) + \min(0.15, 0.01 \cdot N_{assume})$$

Bounded: $0.5 \leq A_{project} \leq 1.2$

### 4.3.3 Component Score Formulas

**Drawing Ingestion Score:**
$$s_{ingestion} = 0.4 \cdot E_{complete} + 0.3 \cdot C_{ocr} + 0.2 \cdot C_{scale} + 0.1 \cdot (1 - R_{error})$$

**Shear Wall Detection Score:**
$$s_{walls} = 0.3 \cdot R_{detect} + 0.3 \cdot R_{schedule} + 0.2 \cdot R_{holdown} + 0.2 \cdot \left(1 - \frac{N_{flags}}{N_{walls}}\right)$$

**Rod Design Score:**
$$s_{rod} = 0.35 \cdot (1 - U_{max}) + 0.25 \cdot A_{shrink} + 0.2 \cdot C_{hardware} + 0.2 \cdot C_{force}$$

**Structural Audit Score:**
$$s_{audit} = 0.5 \cdot \frac{N_{verified}}{N_{total}} + 0.3 \cdot \left(1 - \frac{D_{max}}{T_{tolerance}}\right) + 0.2 \cdot R_{checks}$$

---

## 4.4 Risk Classification

### 4.4.1 Classification Thresholds

| Score Range | Risk Classification | PE Review Intensity |
|-------------|---------------------|---------------------|
| 85-100 | LOW | Standard |
| 70-84 | MODERATE | Enhanced |
| 50-69 | HIGH | Detailed |
| 0-49 | CRITICAL | Full Recalculation |

### 4.4.2 PE Review Recommendations

```python
def recommend_pe_review(self, score: float) -> Dict:
    """Recommend PE review intensity."""
    risk = self.classify_risk(score)

    intensity_map = {
        RiskClassification.LOW: PEReviewIntensity.STANDARD,
        RiskClassification.MODERATE: PEReviewIntensity.ENHANCED,
        RiskClassification.HIGH: PEReviewIntensity.DETAILED,
        RiskClassification.CRITICAL: PEReviewIntensity.FULL_RECALC
    }

    scope_estimates = {
        PEReviewIntensity.STANDARD:
            "Spot-check critical connections, verify governing load case",
        PEReviewIntensity.ENHANCED:
            "Review all rod runs, verify load path, check anchorage design",
        PEReviewIntensity.DETAILED:
            "Full calculation review, verify all assumptions, field-verify drawings",
        PEReviewIntensity.FULL_RECALC:
            "Independent recalculation recommended, significant uncertainty identified"
    }

    return {
        'confidence_score': score,
        'risk_classification': risk.value,
        'review_intensity': intensity_map[risk].value,
        'estimated_scope': scope_estimates[intensity_map[risk]]
    }
```

---

## 4.5 Score Breakdown Output

```python
def generate_score_breakdown(self) -> Dict:
    """Generate detailed score breakdown."""
    overall = self.calculate_overall_score()

    # Calculate sub-scores by category
    data_quality = self._calculate_subscore([
        'drawing_ingestion', 'geometry_normalization'
    ])
    design_confidence = self._calculate_subscore([
        'shear_wall_detection', 'load_path_analysis', 'rod_design'
    ])
    verification_confidence = self._calculate_subscore([
        'code_compliance', 'structural_audit'
    ])
    completeness = self._calculate_subscore([
        'clash_detection', 'revision_tracking'
    ])

    return {
        'overall_score': overall,
        'risk_classification': self.classify_risk(overall).value,
        'component_scores': {
            'data_quality': data_quality,
            'design_confidence': design_confidence,
            'verification_confidence': verification_confidence,
            'completeness': completeness
        },
        'pe_review': self.recommend_pe_review(overall),
        'confidence_factors': {
            'positive': [...],  # Factors boosting confidence
            'negative': [...]   # Factors reducing confidence
        }
    }
```
