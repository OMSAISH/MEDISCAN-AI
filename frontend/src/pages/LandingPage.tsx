import React from 'react';
import { Pill, Activity, ShieldCheck, Database, Layers, ArrowRight, Brain, Search, CheckCircle2, Lock, Cpu } from 'lucide-react';
import { DisclaimerBanner } from '../components/common/DisclaimerBanner';

interface LandingPageProps {
  onNavigate: (view: string) => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onNavigate }) => {
  return (
    <div className="space-y-20 pb-16">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-slate-900 text-white py-20 px-4 sm:px-6 lg:px-8 -mt-6">
        <div className="max-w-5xl mx-auto text-center space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-teal-500/10 border border-teal-500/30 text-teal-400 text-xs font-semibold tracking-wide uppercase">
            <Cpu className="w-3.5 h-3.5" />
            Evidence-Driven Multi-Agent Research Platform
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight leading-tight">
            Accelerate Drug Repurposing <br />
            <span className="text-teal-400">Research with AI</span>
          </h1>

          <p className="text-lg sm:text-xl text-slate-300 max-w-3xl mx-auto font-normal leading-relaxed">
            MediScan AI brings clinical trials, scientific literature, patent landscapes, 
            and market intelligence together into one traceable, evidence-grounded research workflow.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <button
              onClick={() => onNavigate('new-analysis')}
              className="w-full sm:w-auto px-8 py-3.5 rounded-lg bg-teal-600 hover:bg-teal-500 text-white font-bold text-sm shadow-lg shadow-teal-900/30 transition-all flex items-center justify-center gap-2"
            >
              Start Research Analysis
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => onNavigate('methodology')}
              className="w-full sm:w-auto px-8 py-3.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-sm border border-slate-700 transition-all"
            >
              Explore Methodology
            </button>
          </div>

          <div className="pt-8">
            <DisclaimerBanner compact />
          </div>
        </div>
      </section>

      {/* Multi-Agent Architecture */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-3">
          <h2 className="text-xs font-bold uppercase tracking-widest text-teal-600">
            Parallel Specialized Agents
          </h2>
          <h3 className="text-3xl font-extrabold text-slate-900">
            Multi-Domain Evidence Intelligence
          </h3>
          <p className="text-slate-600 text-sm leading-relaxed">
            Rather than relying on generic chatbot hallucinations, MediScan AI deploys four specialized agents 
            that query real biomedical repositories in parallel.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Clinical Agent */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="w-10 h-10 rounded-lg bg-teal-50 border border-teal-200 text-teal-700 flex items-center justify-center mb-4">
              <Activity className="w-5 h-5" />
            </div>
            <h4 className="text-base font-bold text-slate-900 mb-2">Clinical Agent</h4>
            <p className="text-xs text-slate-600 leading-relaxed">
              Queries ClinicalTrials.gov API v2 to extract trial phases, enrollment sizes, recruitment statuses, and structured outcomes.
            </p>
            <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] font-mono text-teal-700 font-semibold">
              40% Scoring Weight
            </div>
          </div>

          {/* Literature Agent */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="w-10 h-10 rounded-lg bg-blue-50 border border-blue-200 text-blue-700 flex items-center justify-center mb-4">
              <Database className="w-5 h-5" />
            </div>
            <h4 className="text-base font-bold text-slate-900 mb-2">Literature Agent</h4>
            <p className="text-xs text-slate-600 leading-relaxed">
              Scans PubMed & Europe PMC to classify study types into an evidence hierarchy (Meta-Analyses, RCTs, Observational studies).
            </p>
            <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] font-mono text-blue-700 font-semibold">
              20% Scoring Weight
            </div>
          </div>

          {/* Patent Agent */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="w-10 h-10 rounded-lg bg-indigo-50 border border-indigo-200 text-indigo-700 flex items-center justify-center mb-4">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h4 className="text-base font-bold text-slate-900 mb-2">Patent Agent</h4>
            <p className="text-xs text-slate-600 leading-relaxed">
              Analyzes USPTO & PatentsView databases to detect active patent families, granted methods of use, and institutional assignees.
            </p>
            <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] font-mono text-indigo-700 font-semibold">
              30% Scoring Weight
            </div>
          </div>

          {/* Market Agent */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="w-10 h-10 rounded-lg bg-amber-50 border border-amber-200 text-amber-700 flex items-center justify-center mb-4">
              <Layers className="w-5 h-5" />
            </div>
            <h4 className="text-base font-bold text-slate-900 mb-2">Market Agent</h4>
            <p className="text-xs text-slate-600 leading-relaxed">
              Inspects FDA Orange Book approvals, generic multi-source availability, and industry vs academic sponsorship ratios.
            </p>
            <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] font-mono text-amber-700 font-semibold">
              10% Scoring Weight
            </div>
          </div>
        </div>
      </section>

      {/* Transparent Scoring & Explainability */}
      <section className="bg-slate-100/70 border-y border-slate-200/80 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-5">
              <span className="text-xs font-bold uppercase tracking-widest text-teal-600">
                Transparent Methodology
              </span>
              <h3 className="text-3xl font-extrabold text-slate-900">
                Explainable Scoring Without Black-Box Magic
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                MediScan AI calculates a transparent 0–100 Evidence Score for every candidate indication. 
                Every single point is accountable to specific clinical trials, publications, or patent records.
              </p>
              
              <ul className="space-y-3 text-xs text-slate-700">
                <li className="flex items-center gap-2.5">
                  <CheckCircle2 className="w-4 h-4 text-teal-600 flex-shrink-0" />
                  <span><strong>Zero Hallucinated Numbers:</strong> Every score is computed via reproducible mathematical formulas.</span>
                </li>
                <li className="flex items-center gap-2.5">
                  <CheckCircle2 className="w-4 h-4 text-teal-600 flex-shrink-0" />
                  <span><strong>Full Traceability:</strong> Click directly through to ClinicalTrials.gov NCT IDs and PubMed PMIDs.</span>
                </li>
                <li className="flex items-center gap-2.5">
                  <CheckCircle2 className="w-4 h-4 text-teal-600 flex-shrink-0" />
                  <span><strong>Evidence Strength Badges:</strong> Categorized as Strong, Moderate, Limited, or Insufficient.</span>
                </li>
              </ul>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-md space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div>
                  <h4 className="font-bold text-slate-900 text-sm">Example: Metformin in Colorectal Neoplasms</h4>
                  <p className="text-xs text-slate-500 font-mono">Discovered Indication Record</p>
                </div>
                <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                  82.5 / 100 • Strong
                </span>
              </div>

              <div className="space-y-2 text-xs">
                <div className="flex justify-between text-slate-600">
                  <span>Clinical Trials (40%)</span>
                  <span className="font-mono font-bold">85.0</span>
                </div>
                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                  <div className="bg-teal-500 h-full w-[85%]"></div>
                </div>

                <div className="flex justify-between text-slate-600 pt-1">
                  <span>Patent Landscape (30%)</span>
                  <span className="font-mono font-bold">78.0</span>
                </div>
                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                  <div className="bg-indigo-500 h-full w-[78%]"></div>
                </div>

                <div className="flex justify-between text-slate-600 pt-1">
                  <span>Scientific Literature (20%)</span>
                  <span className="font-mono font-bold">88.0</span>
                </div>
                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                  <div className="bg-blue-500 h-full w-[88%]"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="max-w-4xl mx-auto px-4 text-center space-y-6">
        <h3 className="text-3xl font-extrabold text-slate-900">
          Ready to Explore Repurposing Candidates?
        </h3>
        <p className="text-slate-600 text-sm max-w-xl mx-auto">
          Start an investigation on compounds like Metformin, Aspirin, Atorvastatin, or Losartan 
          and generate instant pharmaceutical research reports.
        </p>
        <button
          onClick={() => onNavigate('new-analysis')}
          className="px-8 py-3.5 rounded-lg bg-teal-600 hover:bg-teal-500 text-white font-bold text-sm shadow-md transition-colors"
        >
          Launch MediScan Analysis
        </button>
      </section>
    </div>
  );
};
