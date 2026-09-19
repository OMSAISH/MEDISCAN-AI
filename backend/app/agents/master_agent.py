import asyncio
import time
import uuid
import logging
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.models.research import (
    ResearchQuery, 
    AgentRun, 
    DiscoveredIndication, 
    QueryStatus, 
    AgentStatus
)
from backend.app.models.evidence import EvidenceItem, SourceType
from backend.app.agents.clinical_agent import ClinicalAgent
from backend.app.agents.literature_agent import LiteratureAgent
from backend.app.agents.patent_agent import PatentAgent
from backend.app.agents.market_agent import MarketAgent
from backend.app.services.drug_normalizer import drug_normalizer
from backend.app.services.llm_provider import llm_provider
from backend.app.services.event_stream import event_stream_manager
from backend.app.scoring.scoring_engine import scoring_engine
from backend.app.explainability.explainer import explainability_engine

logger = logging.getLogger("mediscan.agents.master")

class MasterAgent:
    """Master Orchestrator Agent for MediScan AI."""

    def __init__(self):
        self.clinical_agent = ClinicalAgent()
        self.literature_agent = LiteratureAgent()
        self.patent_agent = PatentAgent()
        self.market_agent = MarketAgent()

    async def execute_research(
        self,
        db: AsyncSession,
        query_id: str,
        drug_name: str,
        research_question: str = "",
        enable_clinical: bool = True,
        enable_literature: bool = True,
        enable_patent: bool = True,
        enable_market: bool = True
    ):
        overall_start_time = time.time()
        logger.info(f"[MasterAgent] Starting research execution for query {query_id}: {drug_name}")

        # 1. Update query status to RUNNING
        stmt = select(ResearchQuery).where(ResearchQuery.id == query_id)
        result = await db.execute(stmt)
        query = result.scalar_one_or_none()
        if not query:
            logger.error(f"[MasterAgent] Query {query_id} not found in DB.")
            return

        query.status = QueryStatus.RUNNING
        await db.commit()

        await event_stream_manager.publish(query_id, "query_started", {
            "query_id": query_id,
            "drug_name": drug_name,
            "message": "Master Agent initialized. Decomposing research task..."
        })

        # 2. Normalize drug identity
        norm_result = await drug_normalizer.normalize(drug_name)
        canonical_name = norm_result["normalized_name"]
        query.normalized_drug_name = canonical_name
        query.canonical_smiles = norm_result.get("canonical_smiles")
        query.pubchem_cid = norm_result.get("pubchem_cid")
        query.chembl_id = norm_result.get("chembl_id")
        await db.commit()

        # 3. Create agent tasks for concurrent execution
        tasks = []
        agent_names = []

        if enable_clinical:
            tasks.append(self.clinical_agent.run(query_id, canonical_name))
            agent_names.append("Clinical")
        if enable_literature:
            tasks.append(self.literature_agent.run(query_id, canonical_name))
            agent_names.append("Literature")
        if enable_patent:
            tasks.append(self.patent_agent.run(query_id, canonical_name))
            agent_names.append("Patent")
        if enable_market:
            # Market agent will be gathered
            tasks.append(self.market_agent.run(query_id, canonical_name))
            agent_names.append("Market")

        await event_stream_manager.publish(query_id, "agents_launched", {
            "active_agents": agent_names,
            "message": f"Executing {len(tasks)} specialized research agents concurrently..."
        })

        # 4. Execute agents concurrently with asyncio.gather
        results = await asyncio.gather(*tasks, return_exceptions=True)

        clinical_res = {}
        literature_res = {}
        patent_res = {}
        market_res = {}

        has_partial_failure = False

        for name, res in zip(agent_names, results):
            if isinstance(res, Exception):
                has_partial_failure = True
                logger.error(f"[MasterAgent] Agent {name} raised exception: {res}")
                agent_res = {"status": "FAILED", "error": str(res), "execution_time_ms": 0}
            else:
                agent_res = res

            if name == "Clinical":
                clinical_res = agent_res
            elif name == "Literature":
                literature_res = agent_res
            elif name == "Patent":
                patent_res = agent_res
            elif name == "Market":
                market_res = agent_res

            # Record AgentRun in DB
            agent_run = AgentRun(
                id=str(uuid.uuid4()),
                query_id=query_id,
                agent_name=f"{name} Agent",
                status=AgentStatus.COMPLETED if agent_res.get("status") == "COMPLETED" else AgentStatus.FAILED,
                items_found=len(agent_res.get("trials", [])) or len(agent_res.get("publications", [])) or len(agent_res.get("patents", [])) or (1 if agent_res.get("fda_data") else 0),
                execution_time_ms=agent_res.get("execution_time_ms"),
                error_message=agent_res.get("error"),
                details_json={"status": agent_res.get("status")}
            )
            db.add(agent_run)

        await db.commit()

        # 5. Discover indications from evidence
        clinical_groups = clinical_res.get("indication_groups", {})
        literature_groups = literature_res.get("indication_map", {})
        patent_groups = patent_res.get("patent_map", {})
        market_data = market_res.get("market_data", {})

        # Collect all candidate indication names
        all_indication_names = set(clinical_groups.keys()) | set(literature_groups.keys()) | set(patent_groups.keys())
        # Filter out generic/unspecified terms if other indications exist
        if len(all_indication_names) > 1:
            all_indication_names.discard("Unspecified Condition")
            all_indication_names.discard("General Biomedical Research")
            all_indication_names.discard("General Formulation / Drug Delivery")

        discovered_records = []
        all_evidence_items = []

        for ind_name in all_indication_names:
            ind_trials = clinical_groups.get(ind_name, [])
            ind_pubs = literature_groups.get(ind_name, [])
            ind_patents = patent_groups.get(ind_name, [])

            # Phase distribution calculation
            phase_dist: Dict[str, int] = {}
            for t in ind_trials:
                for p in t.get("phases", []):
                    phase_dist[p] = phase_dist.get(p, 0) + 1

            # Calculate scores
            scores = scoring_engine.score_indication(
                trials=ind_trials,
                publications=ind_pubs,
                patents=ind_patents,
                market_data=market_data
            )

            # Generate explainability
            explanation_data = explainability_engine.explain(
                indication_name=ind_name,
                trials=ind_trials,
                publications=ind_pubs,
                patents=ind_patents,
                scores=scores
            )

            indication_id = str(uuid.uuid4())
            ind_record = DiscoveredIndication(
                id=indication_id,
                query_id=query_id,
                indication_name=ind_name,
                evidence_score=scores["evidence_score"],
                clinical_score=scores["clinical_score"],
                literature_score=scores["literature_score"],
                patent_score=scores["patent_score"],
                market_score=scores["market_score"],
                evidence_strength=scores["evidence_strength"],
                clinical_trial_count=len(ind_trials),
                literature_count=len(ind_pubs),
                patent_count=len(ind_patents),
                market_signal_count=len(market_data.get("commercial_signals", [])),
                phase_distribution_json=phase_dist,
                positive_factors_json=explanation_data["positive_factors"],
                limitations_json=explanation_data["limitations"],
                explanation=explanation_data["narrative_explanation"]
            )
            db.add(ind_record)
            discovered_records.append(ind_record)

            # Create Clinical Evidence Items
            for t in ind_trials:
                item = EvidenceItem(
                    id=str(uuid.uuid4()),
                    query_id=query_id,
                    indication_id=indication_id,
                    source_type=SourceType.CLINICAL,
                    source_id=t.get("nct_id", "NCT00000000"),
                    source_url=t.get("source_url", "https://clinicaltrials.gov"),
                    title=t.get("title", ""),
                    publication_date=t.get("phase"),
                    evidence_type=f"{t.get('phase', 'Trial')} ({t.get('status', 'Unknown')})",
                    evidence_strength="Strong" if "PHASE3" in t.get("phases", []) else "Moderate",
                    extracted_facts_json={
                        "enrollment": t.get("enrollment"),
                        "sponsor": t.get("sponsor"),
                        "primary_outcomes": t.get("primary_outcomes"),
                        "summary": t.get("summary")
                    },
                    provenance_json={"provider": "ClinicalTrials.gov", "is_fallback": t.get("is_fallback", False)},
                    confidence=1.0
                )
                db.add(item)
                all_evidence_items.append(item)

            # Create Literature Evidence Items
            for p in ind_pubs:
                item = EvidenceItem(
                    id=str(uuid.uuid4()),
                    query_id=query_id,
                    indication_id=indication_id,
                    source_type=SourceType.LITERATURE,
                    source_id=f"PMID:{p.get('pmid', '')}",
                    source_url=p.get("source_url", "https://pubmed.ncbi.nlm.nih.gov"),
                    title=p.get("title", ""),
                    publication_date=p.get("pub_date"),
                    evidence_type=p.get("study_type", "Journal Article"),
                    evidence_strength="Strong" if p.get("study_type") in ["Meta-Analysis", "Systematic Review"] else "Moderate",
                    extracted_facts_json={
                        "authors": p.get("authors"),
                        "journal": p.get("journal"),
                        "doi": p.get("doi")
                    },
                    provenance_json={"provider": "NCBI PubMed", "is_fallback": p.get("is_fallback", False)},
                    confidence=1.0
                )
                db.add(item)
                all_evidence_items.append(item)

            # Create Patent Evidence Items
            for pat in ind_patents:
                item = EvidenceItem(
                    id=str(uuid.uuid4()),
                    query_id=query_id,
                    indication_id=indication_id,
                    source_type=SourceType.PATENT,
                    source_id=pat.get("patent_number", ""),
                    source_url=pat.get("source_url", "https://patents.google.com"),
                    title=pat.get("title", ""),
                    publication_date=pat.get("date"),
                    evidence_type=f"Patent ({pat.get('jurisdiction', 'US')})",
                    evidence_strength="Moderate",
                    extracted_facts_json={
                        "assignee": pat.get("assignee"),
                        "abstract": pat.get("abstract")
                    },
                    provenance_json={"provider": "PatentsView / Google Patents", "is_fallback": pat.get("is_fallback", False)},
                    confidence=0.9
                )
                db.add(item)
                all_evidence_items.append(item)

        # 6. Generate Executive Synthesis
        total_trials_count = len(clinical_res.get("trials", []))
        total_pubs_count = len(literature_res.get("publications", []))
        total_patents_count = len(patent_res.get("patents", []))
        total_market_count = len(market_data.get("commercial_signals", []))

        synthesis = await llm_provider.synthesize_analysis(
            drug_name=canonical_name,
            research_question=research_question,
            indications=[
                {"indication_name": ind.indication_name, "evidence_score": ind.evidence_score}
                for ind in discovered_records
            ],
            clinical_count=total_trials_count,
            literature_count=total_pubs_count,
            patent_count=total_patents_count,
            market_count=total_market_count
        )

        query.executive_summary = synthesis["executive_summary"]
        query.synthesis_disclaimer = synthesis["disclaimer"]
        query.status = QueryStatus.PARTIAL_FAILURE if has_partial_failure else QueryStatus.COMPLETED
        query.execution_time_ms = int((time.time() - overall_start_time) * 1000)
        
        await db.commit()

        # 7. Notify subscribers of completion
        await event_stream_manager.publish(query_id, "analysis_completed", {
            "query_id": query_id,
            "status": query.status.value,
            "indications_count": len(discovered_records),
            "execution_time_ms": query.execution_time_ms,
            "message": "MediScan AI analysis completed successfully."
        })
        logger.info(f"[MasterAgent] Analysis {query_id} finished in {query.execution_time_ms}ms with {len(discovered_records)} indications.")

master_agent = MasterAgent()
