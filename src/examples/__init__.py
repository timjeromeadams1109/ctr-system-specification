"""
CTR System Example Implementations

This module contains example implementations demonstrating
the core functionality of the CTR design system.

Examples:
    basic_rod_design.py - Rod sizing and capacity calculations
    shrinkage_analysis.py - Wood shrinkage and take-up device selection
    clash_detection.py - 3D spatial indexing and intersection detection
    confidence_scoring.py - Weighted multi-factor scoring model
    full_project_workflow.py - Complete pipeline demonstration
"""

from .basic_rod_design import (
    design_rod_run,
    compute_rod_capacity,
    compute_tension_demand,
    compute_overturning_moment,
    select_rod_diameter,
    RodDesignResult,
    ShearWallInput,
    LoadBasis,
    RodGrade,
)

from .shrinkage_analysis import (
    compute_wood_shrinkage,
    compute_rod_elongation,
    analyze_rod_run_shrinkage,
    ShrinkageAnalysisResult,
    FloorAssembly,
    WoodSpecies,
)

from .clash_detection import (
    ClashDetectionEngine,
    SpatialElement,
    Cylinder,
    Box,
    Point3D,
    BoundingBox,
    ClashResult,
    ElementType,
    ClashSeverity,
)

from .confidence_scoring import (
    ConfidenceScoreEngine,
    ComponentScore,
    ProjectFactors,
    RiskClassification,
    PEReviewIntensity,
)

from .full_project_workflow import (
    CTRProject,
    ProjectConfig,
    ProjectStatus,
)

__all__ = [
    # Rod Design
    'design_rod_run',
    'compute_rod_capacity',
    'compute_tension_demand',
    'compute_overturning_moment',
    'select_rod_diameter',
    'RodDesignResult',
    'ShearWallInput',
    'LoadBasis',
    'RodGrade',

    # Shrinkage
    'compute_wood_shrinkage',
    'compute_rod_elongation',
    'analyze_rod_run_shrinkage',
    'ShrinkageAnalysisResult',
    'FloorAssembly',
    'WoodSpecies',

    # Clash Detection
    'ClashDetectionEngine',
    'SpatialElement',
    'Cylinder',
    'Box',
    'Point3D',
    'BoundingBox',
    'ClashResult',
    'ElementType',
    'ClashSeverity',

    # Confidence Scoring
    'ConfidenceScoreEngine',
    'ComponentScore',
    'ProjectFactors',
    'RiskClassification',
    'PEReviewIntensity',

    # Project Workflow
    'CTRProject',
    'ProjectConfig',
    'ProjectStatus',
]
