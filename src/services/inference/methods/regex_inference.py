import re
from src.services.inference.methods.base import InferenceMethod
from src.models.schemas import InferenceResult, InferredCode, Justification, Audit, now_iso

# HCPCS Level II (alpha + 4 digits) like G0008, A0428, J0120
HCPCS_ALPHA = re.compile(r"\b([A-V][0-9]{4})\b", re.IGNORECASE)

# Contextual CPT: "CPT 99213"
CPT_CONTEXT = re.compile(r"\bCPT(?:®)?\s*([0-9]{5})\b", re.IGNORECASE)

# Contextual ICD-10: "ICD-10 Z00.00" / "ICD10-CM E11.9"
ICD10_CONTEXT = re.compile(
    r"\bICD-?10(?:-CM)?\s*([A-TV-Z][0-9][0-9A-Z](?:\.[0-9A-Z]{1,4})?)\b",
    re.IGNORECASE,
)

class RegexInference(InferenceMethod):
    def infer(self, policy_text: str) -> InferenceResult:
        found = []

        for code in sorted(set(HCPCS_ALPHA.findall(policy_text))):
            c = code.upper()
            found.append(InferredCode(
                code=c,
                code_system="HCPCS",
                confidence=1.0,
                justification=Justification(reason=f"Explicitly mentioned in policy text: {c}")
            ))

        for code in sorted(set(CPT_CONTEXT.findall(policy_text))):
            found.append(InferredCode(
                code=code,
                code_system="CPT",
                confidence=1.0,
                justification=Justification(reason=f"Explicitly mentioned in policy text: CPT {code}")
            ))

        for code in sorted(set(ICD10_CONTEXT.findall(policy_text))):
            c = code.upper()
            found.append(InferredCode(
                code=c,
                code_system="ICD10",
                confidence=1.0,
                justification=Justification(reason=f"Explicitly mentioned in policy text: ICD-10 {c}")
            ))

        audit = Audit(
            timestamp=now_iso(),
            method="regex",
            parameters={"patterns": ["HCPCS_ALPHA", "CPT_CONTEXT", "ICD10_CONTEXT"]},
        )
        return InferenceResult(inferred_codes=found, audit=audit)