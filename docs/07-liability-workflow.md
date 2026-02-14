# Section 7 — Liability and PE Stamp Workflow

## 7.1 Engineering Disclaimer Structure

### 7.1.1 Standard Disclaimer Template

```python
ENGINEERING_DISCLAIMER = """
================================================================================
                        ENGINEERING DISCLAIMER
================================================================================

This continuous rod system design package has been prepared using automated
structural analysis software. The following terms and conditions apply:

1. SCOPE OF AUTOMATED ANALYSIS
   This package includes:
   - Continuous threaded rod sizing and layout
   - Take-up device selection and placement
   - Shrinkage accommodation analysis
   - Foundation anchorage design
   - Clash detection with available MEP information

   This package DOES NOT include:
   - Collector design
   - Diaphragm analysis
   - Foundation design beyond anchor embedment
   - Field verification of actual conditions
   - Construction observation

2. ASSUMPTIONS AND LIMITATIONS
   The design is based on the following assumptions:
   {assumption_list}

   Any deviation from these assumptions may require design modification.

3. DRAWING INTERPRETATION
   This design is based on drawings provided as of {drawing_date}.
   Drawing revision: {revision}
   Confidence score: {confidence_score}/100

4. FIELD VERIFICATION REQUIRED
   Prior to installation, the following must be field-verified:
   - Actual stud and plate sizes match design assumptions
   - Holdown locations are accessible and conflict-free
   - Foundation reinforcement allows anchor placement
   - MEP routing does not conflict with rod runs

5. PROFESSIONAL RESPONSIBILITY
   This design has been prepared under the supervision of:
   {pe_name}, {pe_title}
   License No. {pe_license}
   State: {pe_state}

6. LIMITATION OF LIABILITY
   The liability of the design professional and software provider is limited
   to the scope of services described herein.

================================================================================
"""
```

---

## 7.2 Assumption Logging System

```python
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from enum import Enum

class AssumptionCategory(Enum):
    GEOMETRY = "GEOMETRY"
    MATERIAL = "MATERIAL"
    LOADING = "LOADING"
    CODE = "CODE"
    CONSTRUCTION = "CONSTRUCTION"
    COORDINATION = "COORDINATION"

class AssumptionSource(Enum):
    DRAWING_INFERENCE = "DRAWING_INFERENCE"
    CODE_DEFAULT = "CODE_DEFAULT"
    INDUSTRY_STANDARD = "INDUSTRY_STANDARD"
    USER_INPUT = "USER_INPUT"
    MANUFACTURER_DATA = "MANUFACTURER_DATA"
    ENGINEERING_JUDGMENT = "ENGINEERING_JUDGMENT"

@dataclass
class Assumption:
    """Record of a design assumption."""
    assumption_id: str
    category: AssumptionCategory
    source: AssumptionSource
    description: str
    value: str
    rationale: str
    code_reference: Optional[str] = None
    risk_if_incorrect: str = "Unknown"
    verification_method: str = "Field verification"
    acknowledged: bool = False


class AssumptionLogger:
    """System for logging design assumptions."""

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.assumptions: List[Assumption] = []

    def log_assumption(
        self,
        category: AssumptionCategory,
        source: AssumptionSource,
        description: str,
        value: str,
        rationale: str,
        code_reference: str = None,
        risk_if_incorrect: str = "Unknown"
    ) -> str:
        """Log a new assumption."""
        assumption_id = f"ASMP-{len(self.assumptions)+1:05d}"

        assumption = Assumption(
            assumption_id=assumption_id,
            category=category,
            source=source,
            description=description,
            value=value,
            rationale=rationale,
            code_reference=code_reference,
            risk_if_incorrect=risk_if_incorrect
        )

        self.assumptions.append(assumption)
        return assumption_id


# Standard assumptions
STANDARD_ASSUMPTIONS = [
    {
        'category': AssumptionCategory.MATERIAL,
        'source': AssumptionSource.CODE_DEFAULT,
        'description': 'Wood moisture content',
        'value': 'Initial 19%, Final 12%',
        'rationale': 'Standard S-Green to equilibrium',
        'code_reference': 'NDS 2024 §4.1.4'
    },
    {
        'category': AssumptionCategory.MATERIAL,
        'source': AssumptionSource.CODE_DEFAULT,
        'description': 'Rod material grade',
        'value': 'ASTM A307 Grade A',
        'rationale': 'Standard grade for CTR systems',
        'code_reference': 'AISC 360 Table J3.2'
    },
    {
        'category': AssumptionCategory.CONSTRUCTION,
        'source': AssumptionSource.INDUSTRY_STANDARD,
        'description': 'Holdown offset from wall end',
        'value': '6 inches to centerline',
        'rationale': 'Per manufacturer recommendations',
        'code_reference': 'Simpson catalog'
    },
    {
        'category': AssumptionCategory.LOADING,
        'source': AssumptionSource.CODE_DEFAULT,
        'description': 'Seismic overstrength factor',
        'value': 'Ωo = 3.0',
        'rationale': 'Light-frame wood shear walls',
        'code_reference': 'ASCE 7-22 Table 12.2-1'
    }
]
```

---

## 7.3 Audit Trail Storage

```python
from enum import Enum
import hashlib
import json

class AuditEventType(Enum):
    PROJECT_CREATED = "PROJECT_CREATED"
    DRAWING_UPLOADED = "DRAWING_UPLOADED"
    DESIGN_STARTED = "DESIGN_STARTED"
    DESIGN_COMPLETED = "DESIGN_COMPLETED"
    CALCULATION_RUN = "CALCULATION_RUN"
    MANUAL_OVERRIDE = "MANUAL_OVERRIDE"
    ASSUMPTION_ADDED = "ASSUMPTION_ADDED"
    PE_REVIEW_STARTED = "PE_REVIEW_STARTED"
    PE_REVIEW_COMPLETED = "PE_REVIEW_COMPLETED"
    PE_APPROVAL = "PE_APPROVAL"
    PE_REJECTION = "PE_REJECTION"
    DOCUMENT_GENERATED = "DOCUMENT_GENERATED"
    DOCUMENT_SIGNED = "DOCUMENT_SIGNED"

@dataclass
class AuditEvent:
    """Immutable audit event record."""
    event_id: str
    event_type: AuditEventType
    timestamp: str
    actor_id: str
    actor_type: str  # "SYSTEM", "USER", "PE"
    project_id: str
    action_description: str
    before_state: Optional[Dict] = None
    after_state: Optional[Dict] = None
    previous_event_hash: str = ""
    event_hash: str = ""

    def compute_hash(self) -> str:
        """Compute hash for chain integrity."""
        hash_data = {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'timestamp': self.timestamp,
            'actor_id': self.actor_id,
            'project_id': self.project_id,
            'previous_event_hash': self.previous_event_hash
        }
        return hashlib.sha256(json.dumps(hash_data, sort_keys=True).encode()).hexdigest()


class AuditTrailManager:
    """Manage immutable audit trail with chain integrity."""

    def log_event(
        self,
        event_type: AuditEventType,
        actor_id: str,
        actor_type: str,
        action_description: str,
        before_state: Dict = None,
        after_state: Dict = None
    ) -> AuditEvent:
        """Log an audit event."""
        self._event_count += 1
        event_id = f"EVT-{self.project_id[:8]}-{self._event_count:08d}"

        event = AuditEvent(
            event_id=event_id,
            event_type=event_type,
            timestamp=datetime.utcnow().isoformat() + "Z",
            actor_id=actor_id,
            actor_type=actor_type,
            project_id=self.project_id,
            action_description=action_description,
            before_state=before_state,
            after_state=after_state,
            previous_event_hash=self._last_hash
        )

        event.event_hash = event.compute_hash()
        self._last_hash = event.event_hash
        self.storage.store_event(event)

        return event
```

---

## 7.4 PE Stamp Workflow

```python
class SignatureStatus(Enum):
    UNSIGNED = "UNSIGNED"
    PENDING = "PENDING"
    SIGNED = "SIGNED"
    VERIFIED = "VERIFIED"
    REVOKED = "REVOKED"

class StampType(Enum):
    PRELIMINARY = "PRELIMINARY"
    FOR_PERMIT = "FOR_PERMIT"
    FOR_CONSTRUCTION = "FOR_CONSTRUCTION"
    AS_BUILT = "AS_BUILT"

@dataclass
class PECredentials:
    """Professional Engineer credentials."""
    pe_name: str
    pe_license_number: str
    pe_state: str
    pe_expiration_date: str
    pe_discipline: str
    firm_name: str
    certificate_thumbprint: str

@dataclass
class DocumentSignature:
    """Digital signature on a document."""
    signature_id: str
    document_hash: str
    signer_credentials: PECredentials
    signature_timestamp: str
    stamp_type: StampType
    signature_status: SignatureStatus
    signature_value: str
    certificate_chain: str


class PEStampWorkflow:
    """Manage PE review and stamp workflow."""

    def submit_for_review(
        self,
        document_package: Dict,
        submitter_id: str
    ) -> str:
        """Submit design package for PE review."""
        submission_id = f"SUB-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        self.current_stage = "SUBMITTED"
        return submission_id

    def add_review_comment(
        self,
        reviewer_id: str,
        comment_type: str,
        location: str,
        comment_text: str
    ):
        """Add PE review comment."""
        comment = {
            'comment_id': f"CMT-{len(self.review_comments)+1:04d}",
            'reviewer_id': reviewer_id,
            'comment_type': comment_type,
            'comment_text': comment_text,
            'status': 'OPEN',
            'created_at': datetime.utcnow().isoformat()
        }
        self.review_comments.append(comment)

    def approve_design(
        self,
        pe_credentials: PECredentials,
        stamp_type: StampType,
        document_content: bytes
    ) -> DocumentSignature:
        """PE approval and digital signature."""
        # Verify all comments resolved
        open_comments = [c for c in self.review_comments if c['status'] == 'OPEN']
        if open_comments:
            raise ValueError(f"Cannot approve: {len(open_comments)} open comments")

        # Compute document hash
        document_hash = hashlib.sha256(document_content).hexdigest()

        # Generate signature
        signature = DocumentSignature(
            signature_id=f"SIG-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            document_hash=document_hash,
            signer_credentials=pe_credentials,
            signature_timestamp=datetime.utcnow().isoformat(),
            stamp_type=stamp_type,
            signature_status=SignatureStatus.SIGNED,
            signature_value=self._generate_signature(document_hash, pe_credentials),
            certificate_chain=""
        )

        self.signatures.append(signature)
        self.current_stage = "APPROVED"

        return signature

    def get_workflow_status(self) -> Dict:
        """Get current workflow status."""
        return {
            'current_stage': self.current_stage,
            'total_comments': len(self.review_comments),
            'open_comments': sum(1 for c in self.review_comments if c['status'] == 'OPEN'),
            'signatures': [
                {
                    'signer': s.signer_credentials.pe_name,
                    'stamp_type': s.stamp_type.value,
                    'timestamp': s.signature_timestamp
                }
                for s in self.signatures
            ],
            'ready_for_approval': all(c['status'] != 'OPEN' for c in self.review_comments)
        }
```
