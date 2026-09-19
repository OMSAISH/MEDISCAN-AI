import React from 'react';
import { BookOpen, Layers, CheckCircle2, ShieldAlert, Cpu, ArrowRight, Activity, Database } from 'lucide-react';
import { DisclaimerBanner } from '../components/common/DisclaimerBanner';

export const MethodologyPage: React.FC = () => {
  const steps = [
    {
      num: '01',
      title: 'Drug Normalization & Validation',
      desc: 'Standardizes input strings (brand names, salts, synonyms) into canonical pharmacopeia entities using PubChem PUG-REST, ChEMBL, and RxNorm dictionaries.'
    },
    {
      num: '02',
      title: 'Task Decomposition',
      desc: 'The Master Agent parses the researcher’s target question and formulates discrete hypotheses across clinical, literature, and intellectual property domains.'
    },
    {
      num: '03',
      title: 'Concurrent Specialized Agents',
      desc: 'Four dedicated agents run in parallel using async orchestration: Clinical Agent (ClinicalTrials.gov), Literature Agent (PubMed/PMC), Patent Agent (USPTO), and Market Agent (OpenFDA).'
    },
    {
      num: '04',
      title: 'Evidence Hierarchy Classification',
      desc: 'Publications and trials are classified according to biomedical evidence hierarchies (Meta-Analyses > RCTs > Observational > Preclinical reports).'
    },
    {
      num: '05',
      title: 'Indication Discovery & Clustering',
      desc: 'Maps diseases and conditions co-occurring in trial arms and publications into standardized therapeutic indication clusters.'
    },
    {
      num: '06',
      title: 'Multi-Domain Evidence Scoring',
      desc: 'Calculates a normalized 0–100 Evidence Score using our transparent, weighted formula: 40% Clinical + 30% Patent + 20% Literature + 10% Market.'
    },
    {
      num: '07',
      title: 'Explainability & Factor Attribution',
      desc: 'Identifies positive score drivers (e.g. late-phase completed trials, meta-analyses) and highlights research gaps (e.g. absence of randomized evidence).'
    },
    {
      num: '08',
      title: 'Executive Research Synthesis',
      desc: 'Generates a grounded executive summary strictly rooted in retrieved evidence, with mandatory scientific disclaimer banners.'
    },
    {
      num: '09',
      title: 'Multi-Format Dossier Generation',
      desc: 'Produces publication-ready PDF, HTML, JSON, and CSV research dossiers with complete provenance metadata.'
    },
    {
      num: '10',
      title: 'Provenance & Audit Trail',
      desc: 'Every evidence item preserves its source identifier (NCT ID, PMID, Patent Number) and clickable URL for independent scientist verification.'
    }
  ];

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
      {/* Title */}
      <div className="space-y-3">
        <span className="text-xs font-bold uppercase tracking-widest text-teal-600 font-mono">
          Transparency & Scientific Rigor
        </span>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
          How MediScan AI Works
        </h1>
        <p className="text-sm text-slate-600 leading-relaxed max-w-3xl">
          MediScan AI is not an ungrounded chatbot. It is a systematic evidence-synthesis engine designed 
          for pharmaceutical researchers, clinical scientists, and biotech teams.
        </p>
      </div>

      <DisclaimerBanner />

      {/* Formula Card */}
      <div className="bg-slate-900 text-white rounded-2xl p-8 border border-slate-800 shadow-xl space-y-6">
        <div className="flex items-center gap-2 text-teal-400 text-xs font-bold uppercase tracking-wider">
          <Layers className="w-4 h-4" />
          Reproducible Scoring Formula
        </div>
        <h2 className="text-2xl font-bold tracking-tight">
          Evidence Score Calculation Model
        </h2>
        <div className="bg-slate-800/90 rounded-xl p-5 font-mono text-sm sm:text-base text-teal-300 border border-slate-700">
          Score = 100 × [ 0.40 × Clinical + 0.30 × Patent + 0.20 × Literature + 0.10 × Market ]
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs text-slate-300 pt-2">
          <div className="bg-slate-800/40 p-4 rounded-lg border border-slate-700/60">
            <strong className="text-teal-400 block mb-1">Clinical Trials (40%):</strong>
            Weights trial phase maturity (Phase 3/4 = 0.85–1.0, Phase 2 = 0.60, Phase 1 = 0.35), 
            cohort sample size with log scaling, and completion status.
          </div>

          <div className="bg-slate-800/40 p-4 rounded-lg border border-slate-700/60">
            <strong className="text-indigo-400 block mb-1">Patent Landscape (30%):</strong>
            Evaluates granted patents versus applications, assignee diversity, and intellectual property exclusivity signals.
          </div>

          <div className="bg-slate-800/40 p-4 rounded-lg border border-slate-700/60">
            <strong className="text-blue-400 block mb-1">Scientific Literature (20%):</strong>
            Prioritizes meta-analyses (1.0), randomized controlled trials (0.85), and observational cohorts (0.50).
          </div>

          <div className="bg-slate-800/40 p-4 rounded-lg border border-slate-700/60">
            <strong className="text-amber-400 block mb-1">Market & Regulatory (10%):</strong>
            Identifies FDA approved labeling, generic availability, and industry versus academic sponsorship ratios.
          </div>
        </div>
      </div>

      {/* 10-Step Workflow */}
      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-slate-900">
          The 10-Step Evidence Synthesis Pipeline
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {steps.map((s) => (
            <div key={s.num} className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-2">
              <span className="font-mono text-xs font-extrabold text-teal-600 bg-teal-50 px-2 py-0.5 rounded">
                STEP {s.num}
              </span>
              <h3 className="font-bold text-slate-900 text-sm">{s.title}</h3>
              <p className="text-xs text-slate-600 leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Scientific Rules */}
      <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6 sm:p-8 space-y-4">
        <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-teal-600" />
          Strict Scientific Ethics & Operating Boundaries
        </h3>
        <ul className="space-y-2.5 text-xs text-slate-700">
          <li className="flex items-start gap-2">
            <CheckCircle2 className="w-4 h-4 text-teal-600 flex-shrink-0 mt-0.5" />
            <span><strong>Never claim medical cure or efficacy:</strong> Evidence scores reflect research activity density, not validated biological efficacy.</span>
          </li>
          <li className="flex items-start gap-2">
            <CheckCircle2 className="w-4 h-4 text-teal-600 flex-shrink-0 mt-0.5" />
            <span><strong>Zero fabrication:</strong> If an API or source returns no data, MediScan AI reports "Unavailable" rather than inventing numbers.</span>
          </li>
          <li className="flex items-start gap-2">
            <CheckCircle2 className="w-4 h-4 text-teal-600 flex-shrink-0 mt-0.5" />
            <span><strong>Provenance preservation:</strong> Every clinical trial, paper, and patent record maintains a direct clickable link to official registries.</span>
          </li>
        </ul>
      </div>
    </div>
  );
};
