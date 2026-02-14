"""
Confidence Scoring Example

Demonstrates the weighted multi-factor confidence scoring model
for CTR design projects.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
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
    """Score contribution from a single pipeline component."""
    component_name: str
    base_weight: float
    raw_score: float  # 0-1
    penalty_factor: float = 1.0
    flags: List[str] = field(default_factory=list)
    details: str = ""

    @property
    def weighted_contribution(self) -> float:
        """Calculate weighted score contribution."""
        return self.base_weight * self.raw_score * self.penalty_factor

    @property
    def effective_score(self) -> float:
        """Calculate effective score after penalties."""
        return self.raw_score * self.penalty_factor


@dataclass
class ProjectFactors:
    """Project-level factors affecting confidence."""
    drawing_clarity: float  # 0-1 (1 = crystal clear)
    schedule_completeness: float  # 0-1 (1 = all data present)
    load_path_continuity: float  # 0-1 (1 = perfect continuity)
    conflict_density: float  # clashes per rod run
    code_compliance_certainty: float  # 0-1
    ambiguity_count: int  # number of ambiguous interpretations
    assumption_count: int  # number of assumptions made
    manual_override_count: int  # number of manual corrections


class ConfidenceScoreEngine:
    """Calculate overall project confidence score."""

    # Component weights (sum > 1.0 allows bonus scoring)
    COMPONENT_WEIGHTS = {
        'drawing_ingestion': 0.15,
        'geometry_normalization': 0.10,
        'shear_wall_detection': 0.20,
        'load_path_analysis': 0.15,
        'rod_design': 0.20,
        'clash_detection': 0.05,
        'code_compliance': 0.10,
        'structural_audit': 0.15,
        'revision_tracking': 0.02,
    }

    def __init__(self):
        self.component_scores: Dict[str, ComponentScore] = {}
        self.project_factors: Optional[ProjectFactors] = None

    def add_component_score(
        self,
        component_name: str,
        raw_score: float,
        penalty_factor: float = 1.0,
        flags: List[str] = None,
        details: str = ""
    ):
        """Add a component score."""
        if component_name not in self.COMPONENT_WEIGHTS:
            raise ValueError(f"Unknown component: {component_name}")

        self.component_scores[component_name] = ComponentScore(
            component_name=component_name,
            base_weight=self.COMPONENT_WEIGHTS[component_name],
            raw_score=raw_score,
            penalty_factor=penalty_factor,
            flags=flags or [],
            details=details
        )

    def set_project_factors(self, factors: ProjectFactors):
        """Set project-level adjustment factors."""
        self.project_factors = factors

    def _calculate_factor_adjustment(self) -> float:
        """Calculate adjustment multiplier from project factors."""
        if not self.project_factors:
            return 1.0

        pf = self.project_factors

        # Positive factors (boost score)
        positive = (
            0.10 * pf.drawing_clarity +
            0.10 * pf.schedule_completeness +
            0.15 * pf.load_path_continuity +
            0.10 * pf.code_compliance_certainty
        )

        # Negative factors (reduce score)
        conflict_penalty = min(0.20, pf.conflict_density * 0.05)
        ambiguity_penalty = min(0.15, pf.ambiguity_count * 0.01)
        assumption_penalty = min(0.15, pf.assumption_count * 0.01)
        override_penalty = min(0.10, pf.manual_override_count * 0.02)

        negative = (
            conflict_penalty +
            ambiguity_penalty +
            assumption_penalty +
            override_penalty
        )

        # Bounded adjustment factor
        adjustment = 1.0 + positive - negative
        return max(0.5, min(1.2, adjustment))

    def calculate_overall_score(self) -> float:
        """Calculate overall confidence score (0-100)."""
        if not self.component_scores:
            return 0.0

        # Sum weighted contributions
        raw_total = sum(
            cs.weighted_contribution
            for cs in self.component_scores.values()
        )

        # Sum actual weights used
        total_weight = sum(
            cs.base_weight
            for cs in self.component_scores.values()
        )

        # Normalize
        normalized_score = raw_total / total_weight if total_weight > 0 else 0

        # Apply project factor adjustment
        factor_adjustment = self._calculate_factor_adjustment()
        adjusted_score = normalized_score * factor_adjustment

        # Convert to 0-100 scale and bound
        return min(100, max(0, adjusted_score * 100))

    def classify_risk(self, score: float) -> RiskClassification:
        """Classify risk level based on score."""
        if score >= 85:
            return RiskClassification.LOW
        elif score >= 70:
            return RiskClassification.MODERATE
        elif score >= 50:
            return RiskClassification.HIGH
        else:
            return RiskClassification.CRITICAL

    def recommend_pe_review(self, score: float) -> Dict:
        """Generate PE review recommendation."""
        risk = self.classify_risk(score)

        intensity_map = {
            RiskClassification.LOW: PEReviewIntensity.STANDARD,
            RiskClassification.MODERATE: PEReviewIntensity.ENHANCED,
            RiskClassification.HIGH: PEReviewIntensity.DETAILED,
            RiskClassification.CRITICAL: PEReviewIntensity.FULL_RECALC,
        }

        scope_descriptions = {
            PEReviewIntensity.STANDARD: (
                "Spot-check critical connections, verify governing load case, "
                "review representative calculations"
            ),
            PEReviewIntensity.ENHANCED: (
                "Review all rod runs, verify load path continuity, "
                "check anchorage design, validate shrinkage calculations"
            ),
            PEReviewIntensity.DETAILED: (
                "Full calculation review, verify all assumptions, "
                "field-verify drawing interpretations, check all code references"
            ),
            PEReviewIntensity.FULL_RECALC: (
                "Independent recalculation recommended, significant uncertainty "
                "identified, manual verification of all inputs required"
            ),
        }

        time_estimates = {
            PEReviewIntensity.STANDARD: "2-4 hours",
            PEReviewIntensity.ENHANCED: "4-8 hours",
            PEReviewIntensity.DETAILED: "1-2 days",
            PEReviewIntensity.FULL_RECALC: "2-5 days",
        }

        intensity = intensity_map[risk]

        return {
            'confidence_score': round(score, 1),
            'risk_classification': risk.value,
            'review_intensity': intensity.value,
            'estimated_scope': scope_descriptions[intensity],
            'estimated_time': time_estimates[intensity],
        }

    def _calculate_subscore(self, component_names: List[str]) -> float:
        """Calculate subscore for a group of components."""
        relevant = [
            cs for cs in self.component_scores.values()
            if cs.component_name in component_names
        ]

        if not relevant:
            return 0.0

        total_weight = sum(cs.base_weight for cs in relevant)
        weighted_sum = sum(cs.weighted_contribution for cs in relevant)

        return (weighted_sum / total_weight * 100) if total_weight > 0 else 0

    def generate_score_breakdown(self) -> Dict:
        """Generate detailed score breakdown."""
        overall = self.calculate_overall_score()

        # Calculate category subscores
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

        # Identify positive and negative factors
        positive_factors = []
        negative_factors = []

        for cs in self.component_scores.values():
            if cs.effective_score >= 0.9:
                positive_factors.append({
                    'component': cs.component_name,
                    'score': cs.effective_score,
                    'details': cs.details or "High confidence"
                })
            elif cs.effective_score < 0.7:
                negative_factors.append({
                    'component': cs.component_name,
                    'score': cs.effective_score,
                    'flags': cs.flags,
                    'details': cs.details or "Reduced confidence"
                })

        if self.project_factors:
            pf = self.project_factors
            if pf.drawing_clarity >= 0.9:
                positive_factors.append({
                    'component': 'project_factors',
                    'score': pf.drawing_clarity,
                    'details': "High drawing clarity"
                })
            if pf.conflict_density > 2:
                negative_factors.append({
                    'component': 'project_factors',
                    'score': 1 - min(1, pf.conflict_density * 0.1),
                    'details': f"High clash density ({pf.conflict_density} per rod)"
                })

        return {
            'overall_score': round(overall, 1),
            'risk_classification': self.classify_risk(overall).value,
            'category_scores': {
                'data_quality': round(data_quality, 1),
                'design_confidence': round(design_confidence, 1),
                'verification_confidence': round(verification_confidence, 1),
                'completeness': round(completeness, 1),
            },
            'component_details': {
                name: {
                    'raw_score': round(cs.raw_score * 100, 1),
                    'penalty_factor': cs.penalty_factor,
                    'effective_score': round(cs.effective_score * 100, 1),
                    'weight': cs.base_weight,
                    'contribution': round(cs.weighted_contribution * 100, 1),
                    'flags': cs.flags,
                }
                for name, cs in self.component_scores.items()
            },
            'factor_adjustment': round(self._calculate_factor_adjustment(), 3),
            'positive_factors': positive_factors,
            'negative_factors': negative_factors,
            'pe_review': self.recommend_pe_review(overall),
        }


def print_score_breakdown(breakdown: Dict):
    """Print formatted score breakdown."""
    print("\n" + "=" * 70)
    print("CONFIDENCE SCORE BREAKDOWN")
    print("=" * 70)

    print(f"\nOverall Score: {breakdown['overall_score']}/100")
    print(f"Risk Classification: {breakdown['risk_classification']}")
    print(f"Factor Adjustment: {breakdown['factor_adjustment']}")

    print("\n" + "-" * 70)
    print("Category Scores:")
    print("-" * 70)
    for category, score in breakdown['category_scores'].items():
        bar_length = int(score / 2)
        bar = "#" * bar_length + "-" * (50 - bar_length)
        print(f"  {category.replace('_', ' ').title():<25} [{bar}] {score:.1f}")

    print("\n" + "-" * 70)
    print("Component Details:")
    print("-" * 70)
    print(f"{'Component':<25}{'Raw':<8}{'Penalty':<10}{'Effective':<12}{'Weight'}")
    print("-" * 70)

    for name, details in breakdown['component_details'].items():
        print(f"{name:<25}{details['raw_score']:<8.1f}"
              f"{details['penalty_factor']:<10.2f}"
              f"{details['effective_score']:<12.1f}"
              f"{details['weight']:.2f}")
        if details['flags']:
            for flag in details['flags']:
                print(f"  └─ FLAG: {flag}")

    if breakdown['positive_factors']:
        print("\n" + "-" * 70)
        print("Positive Factors:")
        print("-" * 70)
        for factor in breakdown['positive_factors']:
            print(f"  + {factor['component']}: {factor['details']}")

    if breakdown['negative_factors']:
        print("\n" + "-" * 70)
        print("Negative Factors:")
        print("-" * 70)
        for factor in breakdown['negative_factors']:
            print(f"  - {factor['component']}: {factor['details']}")

    print("\n" + "-" * 70)
    print("PE Review Recommendation:")
    print("-" * 70)
    pe = breakdown['pe_review']
    print(f"  Review Intensity: {pe['review_intensity']}")
    print(f"  Estimated Time: {pe['estimated_time']}")
    print(f"  Scope: {pe['estimated_scope']}")
    print()


# Example usage
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("CTR SYSTEM - CONFIDENCE SCORING EXAMPLE")
    print("=" * 70)

    # Create scoring engine
    engine = ConfidenceScoreEngine()

    # Scenario 1: Good project with minor issues
    print("\n\n" + "=" * 70)
    print("SCENARIO 1: Well-Documented Project")
    print("=" * 70)

    engine = ConfidenceScoreEngine()

    # Add component scores
    engine.add_component_score(
        'drawing_ingestion',
        raw_score=0.92,
        details="All drawings parsed successfully, good resolution"
    )
    engine.add_component_score(
        'geometry_normalization',
        raw_score=0.95,
        details="Grid system detected, coordinates aligned"
    )
    engine.add_component_score(
        'shear_wall_detection',
        raw_score=0.88,
        penalty_factor=0.95,
        flags=["2 walls required manual confirmation"],
        details="48/50 walls auto-detected"
    )
    engine.add_component_score(
        'load_path_analysis',
        raw_score=0.90,
        details="All load paths continuous"
    )
    engine.add_component_score(
        'rod_design',
        raw_score=0.94,
        details="All rods within capacity, max utilization 0.89"
    )
    engine.add_component_score(
        'clash_detection',
        raw_score=0.85,
        flags=["3 minor clearance violations"],
        details="No critical clashes"
    )
    engine.add_component_score(
        'code_compliance',
        raw_score=0.98,
        details="All code checks passed"
    )
    engine.add_component_score(
        'structural_audit',
        raw_score=0.92,
        details="Dual-pass verification within tolerance"
    )
    engine.add_component_score(
        'revision_tracking',
        raw_score=0.90,
        details="Initial submission, no revisions"
    )

    # Set project factors
    engine.set_project_factors(ProjectFactors(
        drawing_clarity=0.90,
        schedule_completeness=0.95,
        load_path_continuity=0.92,
        conflict_density=0.5,
        code_compliance_certainty=0.98,
        ambiguity_count=2,
        assumption_count=5,
        manual_override_count=1
    ))

    breakdown = engine.generate_score_breakdown()
    print_score_breakdown(breakdown)

    # Scenario 2: Project with significant issues
    print("\n\n" + "=" * 70)
    print("SCENARIO 2: Problematic Project")
    print("=" * 70)

    engine2 = ConfidenceScoreEngine()

    engine2.add_component_score(
        'drawing_ingestion',
        raw_score=0.72,
        penalty_factor=0.85,
        flags=["Low resolution PDFs", "OCR errors in schedules"],
        details="Scale detection uncertain"
    )
    engine2.add_component_score(
        'geometry_normalization',
        raw_score=0.65,
        penalty_factor=0.90,
        flags=["Grid spacing inconsistent"],
        details="Manual grid alignment required"
    )
    engine2.add_component_score(
        'shear_wall_detection',
        raw_score=0.68,
        penalty_factor=0.80,
        flags=[
            "15 walls ambiguous",
            "Schedule mismatch",
            "Missing holdown symbols"
        ],
        details="Only 35/50 walls confidently identified"
    )
    engine2.add_component_score(
        'load_path_analysis',
        raw_score=0.70,
        flags=["2 discontinuous load paths"],
        details="Collector requirements unclear"
    )
    engine2.add_component_score(
        'rod_design',
        raw_score=0.75,
        flags=["High utilization on 3 rods"],
        details="Max utilization 0.97"
    )
    engine2.add_component_score(
        'clash_detection',
        raw_score=0.55,
        penalty_factor=0.80,
        flags=["2 critical clashes", "MEP model incomplete"],
        details="Incomplete clash analysis"
    )
    engine2.add_component_score(
        'code_compliance',
        raw_score=0.78,
        flags=["Aspect ratio review needed"],
        details="2 walls at code limit"
    )
    engine2.add_component_score(
        'structural_audit',
        raw_score=0.72,
        penalty_factor=0.90,
        flags=["Verification discrepancy on 2 rods"],
        details="Results differ by 4.5%"
    )
    engine2.add_component_score(
        'revision_tracking',
        raw_score=0.60,
        flags=["Revision history unclear"],
        details="Multiple undated revisions"
    )

    engine2.set_project_factors(ProjectFactors(
        drawing_clarity=0.60,
        schedule_completeness=0.70,
        load_path_continuity=0.72,
        conflict_density=3.5,
        code_compliance_certainty=0.78,
        ambiguity_count=15,
        assumption_count=22,
        manual_override_count=8
    ))

    breakdown2 = engine2.generate_score_breakdown()
    print_score_breakdown(breakdown2)

    # Comparison summary
    print("\n" + "=" * 70)
    print("SCENARIO COMPARISON")
    print("=" * 70)
    print(f"\n{'Metric':<30}{'Scenario 1':<20}{'Scenario 2'}")
    print("-" * 70)
    print(f"{'Overall Score':<30}{breakdown['overall_score']:<20}{breakdown2['overall_score']}")
    print(f"{'Risk Classification':<30}{breakdown['risk_classification']:<20}{breakdown2['risk_classification']}")
    print(f"{'PE Review Intensity':<30}{breakdown['pe_review']['review_intensity']:<20}{breakdown2['pe_review']['review_intensity']}")
    print(f"{'Estimated Review Time':<30}{breakdown['pe_review']['estimated_time']:<20}{breakdown2['pe_review']['estimated_time']}")
    print()
