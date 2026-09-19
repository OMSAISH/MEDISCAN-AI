import logging
from typing import Dict, Any, List, Optional
import httpx

logger = logging.getLogger("mediscan.services.drug_normalizer")

# Known common drug aliases dictionary for instant high-accuracy resolution
DRUG_SYNONYMS = {
    "metformin": {
        "canonical_name": "Metformin",
        "synonyms": ["Glucophage", "Fortamet", "Glumetza", "Riomet", "Metformin Hydrochloride", "1,1-Dimethylbiguanide"],
        "pubchem_cid": "4091",
        "chembl_id": "CHEMBL1431",
        "canonical_smiles": "CN(C)C(=N)NC(=N)N",
        "known_indications": ["Type 2 Diabetes Mellitus", "Insulin Resistance", "Polycystic Ovary Syndrome (PCOS)"],
        "therapeutic_class": "Biguanide Antidiabetic Agent"
    },
    "aspirin": {
        "canonical_name": "Aspirin",
        "synonyms": ["Acetylsalicylic Acid", "ASA", "Bayer", "Bufferin", "Ecotrin"],
        "pubchem_cid": "2244",
        "chembl_id": "CHEMBL25",
        "canonical_smiles": "CC(=O)Oc1ccccc1C(=O)O",
        "known_indications": ["Pain", "Inflammation", "Fever", "Cardiovascular Thromboprophylaxis"],
        "therapeutic_class": "Non-Steroidal Anti-Inflammatory Drug (NSAID) / Antiplatelet"
    },
    "atorvastatin": {
        "canonical_name": "Atorvastatin",
        "synonyms": ["Lipitor", "Atorvastatin Calcium", "Sortis"],
        "pubchem_cid": "60823",
        "chembl_id": "CHEMBL1487",
        "canonical_smiles": "CC(C)c1c(C(=O)Nc2ccccc2)c(-c2ccccc2)c(-c2ccc(F)cc2)n1CC[C@@H](O)C[C@@H](O)CC(=O)O",
        "known_indications": ["Hypercholesterolemia", "Prevention of Cardiovascular Disease"],
        "therapeutic_class": "HMG-CoA Reductase Inhibitor (Statin)"
    },
    "losartan": {
        "canonical_name": "Losartan",
        "synonyms": ["Cozaar", "Losartan Potassium"],
        "pubchem_cid": "3961",
        "chembl_id": "CHEMBL1389",
        "canonical_smiles": "CCCCc1nc(Cl)c(CO)n1Cc1ccc(-c2ccccc2-c2nn[nH]n2)cc1",
        "known_indications": ["Hypertension", "Diabetic Nephropathy"],
        "therapeutic_class": "Angiotensin II Receptor Blocker (ARB)"
    },
    "rapamycin": {
        "canonical_name": "Sirolimus",
        "synonyms": ["Rapamycin", "Rapamune"],
        "pubchem_cid": "5284616",
        "chembl_id": "CHEMBL410",
        "canonical_smiles": "CO[C@@H]1C[C@@H]2CC[C@@H](C)[C@@](O)(O2)C(=O)C(=O)N2CCCC[C@H]2C(=O)O[C@@H]([C@H](C)C[C@H]2CC[C@H](O)[C@@H](OC)C2)CC(=O)[C@H](C)/C=C(/C)[C@@H](O)[C@@H](OC)/C=C/C=C/C=C/[C@@H]1C",
        "known_indications": ["Organ Transplant Rejection Prophylaxis", "Lymphangioleiomyomatosis"],
        "therapeutic_class": "mTOR Inhibitor / Immunosuppressant"
    }
}

class DrugNormalizer:
    """Normalizes drug names to canonical chemical entities using local dictionary and PubChem PUG-REST."""

    async def normalize(self, input_name: str) -> Dict[str, Any]:
        cleaned = input_name.strip()
        lower_name = cleaned.lower()

        # 1. Check local high-confidence synonyms dictionary
        for key, info in DRUG_SYNONYMS.items():
            if lower_name == key or lower_name in [s.lower() for s in info["synonyms"]]:
                return {
                    "is_valid": True,
                    "input_name": cleaned,
                    "normalized_name": info["canonical_name"],
                    "synonyms": info["synonyms"],
                    "pubchem_cid": info["pubchem_cid"],
                    "chembl_id": info["chembl_id"],
                    "canonical_smiles": info["canonical_smiles"],
                    "known_indications": info["known_indications"],
                    "therapeutic_class": info["therapeutic_class"],
                    "warnings": []
                }

        # 2. Query PubChem PUG-REST API dynamically
        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{cleaned}/property/Title,InChIKey,CanonicalSMILES/JSON"
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    props = data.get("PropertyTable", {}).get("Properties", [])
                    if props:
                        prop = props[0]
                        cid = str(prop.get("CID", ""))
                        title = prop.get("Title", cleaned.capitalize())
                        smiles = prop.get("CanonicalSMILES", "")
                        return {
                            "is_valid": True,
                            "input_name": cleaned,
                            "normalized_name": title,
                            "synonyms": [cleaned],
                            "pubchem_cid": cid,
                            "chembl_id": None,
                            "canonical_smiles": smiles,
                            "known_indications": [],
                            "therapeutic_class": "Small Molecule Compound",
                            "warnings": ["Dynamically resolved via PubChem PUG-REST."]
                        }
        except Exception as e:
            logger.warning(f"PubChem lookup failed for '{cleaned}': {e}")

        # 3. Fallback: if not found, accept capitalized input with an ambiguity warning
        return {
            "is_valid": len(cleaned) >= 2,
            "input_name": cleaned,
            "normalized_name": cleaned.capitalize(),
            "synonyms": [],
            "pubchem_cid": None,
            "chembl_id": None,
            "canonical_smiles": None,
            "known_indications": [],
            "therapeutic_class": "Unclassified Compound",
            "warnings": [f"'{cleaned}' was not verified against standard pharmacopeia. Proceeding with literal name."]
        }

drug_normalizer = DrugNormalizer()
