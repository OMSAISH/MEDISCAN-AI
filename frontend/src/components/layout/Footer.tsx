import React from 'react';
import { Pill, ShieldCheck, Database, FileText } from 'lucide-react';

export const Footer: React.FC<{ onNavigate?: (view: string) => void }> = ({ onNavigate }) => {
  return (
    <footer className="bg-slate-900 border-t border-slate-800 text-slate-400 text-xs py-10 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-white font-bold text-base">
              <Pill className="w-5 h-5 text-teal-400" />
              <span>MEDISCAN AI</span>
            </div>
            <p className="text-slate-400 leading-relaxed text-xs">
              AI-Powered Evidence Synthesis & Multi-Domain Drug Repurposing Research Intelligence.
            </p>
          </div>

          <div>
            <h4 className="text-white font-semibold mb-3 uppercase tracking-wider text-[11px]">Integrated Repositories</h4>
            <ul className="space-y-2 text-xs">
              <li className="flex items-center gap-1.5"><Database className="w-3.5 h-3.5 text-teal-400" /> ClinicalTrials.gov (API v2)</li>
              <li className="flex items-center gap-1.5"><FileText className="w-3.5 h-3.5 text-teal-400" /> NCBI PubMed & Europe PMC</li>
              <li className="flex items-center gap-1.5"><ShieldCheck className="w-3.5 h-3.5 text-teal-400" /> USPTO & PatentsView</li>
              <li className="flex items-center gap-1.5"><Database className="w-3.5 h-3.5 text-teal-400" /> OpenFDA & Orange Book</li>
            </ul>
          </div>

          <div>
            <h4 className="text-white font-semibold mb-3 uppercase tracking-wider text-[11px]">Platform</h4>
            <ul className="space-y-2 text-xs">
              <li>
                <button onClick={() => onNavigate?.('methodology')} className="hover:text-teal-400 transition-colors">
                  Scoring Methodology
                </button>
              </li>
              <li>
                <button onClick={() => onNavigate?.('dashboard')} className="hover:text-teal-400 transition-colors">
                  Research Dashboard
                </button>
              </li>
              <li>
                <button onClick={() => onNavigate?.('new-analysis')} className="hover:text-teal-400 transition-colors">
                  New Compound Analysis
                </button>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-white font-semibold mb-3 uppercase tracking-wider text-[11px]">Scientific Ethics</h4>
            <p className="text-slate-400 text-xs leading-relaxed">
              Designed with strict evidence-grounding constraints. No clinical efficacy or medical advice claims. All findings traceable to public provenance.
            </p>
          </div>
        </div>

        <div className="pt-6 border-t border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-4 text-[11px]">
          <p>© {new Date().getFullYear()} MediScan AI. Academic & Pharmaceutical Research Intelligence.</p>
          <p className="text-slate-500">Intended strictly for scientific decision-support and hypothesis generation.</p>
        </div>
      </div>
    </footer>
  );
};
