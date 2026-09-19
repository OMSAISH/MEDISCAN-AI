from typing import List, Optional
from fastapi import APIRouter, Query, Depends
from backend.app.services.drug_normalizer import drug_normalizer, DRUG_SYNONYMS
from backend.app.schemas.research import DrugValidationResponse

router = APIRouter(prefix="/drugs", tags=["Drugs"])

@router.get("/validate", response_model=DrugValidationResponse)
async def validate_drug(name: str = Query(..., min_length=1, description="Drug name to normalize and validate")):
    result = await drug_normalizer.normalize(name)
    return DrugValidationResponse(**result)

@router.get("/search")
async def search_drugs(q: Optional[str] = Query(None, description="Search query")):
    if not q:
        return list(DRUG_SYNONYMS.keys())
    
    q_lower = q.lower().strip()
    matches = []
    for key, info in DRUG_SYNONYMS.items():
        if q_lower in key or any(q_lower in s.lower() for s in info["synonyms"]):
            matches.append({
                "canonical_name": info["canonical_name"],
                "synonyms": info["synonyms"],
                "class": info["therapeutic_class"]
            })
    return matches
