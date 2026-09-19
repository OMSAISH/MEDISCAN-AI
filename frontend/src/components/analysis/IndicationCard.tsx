import React, { useState } from 'react';
import { Stethoscope, BookOpen, ShieldAlert, TrendingUp, ChevronDown, ChevronUp, Layers, HelpCircle, FileText } from 'lucide-react';
import { Indication } from '../../types';
import { EvidenceStrengthBadge } from '../common/Badge';
import { EvidenceScoreBreakdown } from './EvidenceScoreBreakdown';
import { ExplainabilityPanel } from './ExplainabilityPanel';

interface IndicationCardProps {
  indication: Indication;
  onViewEvidence: (id: string, name: string) => void;
  onGenerateReport?: () => void;
}

export const IndicationCard: React.FC<IndicationCardProps> = ({
  indication,
  onViewEvidence,
  onGenerateReport
}) => {
  const [showBreakdown, setShowBreakdown] = useState(false);
  const [showExplain, setShowExplain] = useState(false);

  const getScoreColor = (score: number) => {
    if (score >= 75) return 'text-emerald-600 border-emerald-500 bg-emerald-50/50';
    if (score >= 50) return 'text-blue-600 border-blue-500 bg-blue-50/50';
    if (score >= 25) return 'text-amber-600 border-amber-500 bg-amber-50/50';
    return 'text-slate-500 border-slate-300 bg-slate-50';
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-all overflow-hidden">
      <div className="p-6">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="text-lg font-bold text-slate-900">{indication.indication_name}</h3>
              <EvidenceStrengthBadge strength={indication.evidence_strength} />
            </div>
            {indication.therapeutic_area && (
              <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold">
                {indication.therapeutic_area}
              </p>
            )}
          </div>

          {/* Evidence Score Pill */}
          <div className="flex items-center gap-3 self-start sm:self-auto">
            <div className={`px-3 py-1.5 rounded-xl border flex flex-col items-center justify-center ${getScoreColor(indication.evidence_score)}`}>
              <span className="text-[10px] font-bold uppercase tracking-wider">Evidence Score</span>
              <span className="text-xl font-extrabold font-mono">
                {indication.evidence_score.toFixed(1)}
              </span>
            </div>
          </div>
        </div>

        {/* Counts Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-5 pt-4 border-t border-slate-100 text-xs">
          <div className="bg-slate-50 rounded-lg p-2.5 flex items-center gap-2.5">
            <Stethoscope className="w-4 h-4 text-teal-600" />
            <div>
              <span className="text-slate-400 block text-[10px] uppercase">Trials</span>
              <span className="font-bold text-slate-900 text-sm">{indication.clinical_trial_count}</span>
            </div>
          </div>

          <div className="bg-slate-50 rounded-lg p-2.5 flex items-center gap-2.5">
            <BookOpen className="w-4 h-4 text-blue-600" />
            <div>
              <span className="text-slate-400 block text-[10px] uppercase">Publications</span>
              <span className="font-bold text-slate-900 text-sm">{indication.literature_count}</span>
            </div>
          </div>

          <div className="bg-slate-50 rounded-lg p-2.5 flex items-center gap-2.5">
            <ShieldAlert className="w-4 h-4 text-indigo-600" />
            <div>
              <span className="text-slate-400 block text-[10px] uppercase">Patents</span>
              <span className="font-bold text-slate-900 text-sm">{indication.patent_count}</span>
            </div>
          </div>

          <div className="bg-slate-50 rounded-lg p-2.5 flex items-center gap-2.5">
            <TrendingUp className="w-4 h-4 text-amber-600" />
            <div>
              <span className="text-slate-400 block text-[10px] uppercase">Market Signals</span>
              <span className="font-bold text-slate-900 text-sm">{indication.market_signal_count}</span>
            </div>
          </div>
        </div>

        {/* Actions bar */}
        <div className="flex flex-wrap items-center justify-between gap-3 mt-5 pt-4 border-t border-slate-100">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowBreakdown(!showBreakdown)}
              className="text-xs font-semibold text-slate-600 hover:text-slate-900 flex items-center gap-1 px-2.5 py-1.5 rounded-md hover:bg-slate-100 transition-colors"
            >
              <Layers className="w-3.5 h-3.5 text-teal-600" />
              Score Breakdown
              {showBreakdown ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>

            <button
              onClick={() => setShowExplain(!showExplain)}
              className="text-xs font-semibold text-slate-600 hover:text-slate-900 flex items-center gap-1 px-2.5 py-1.5 rounded-md hover:bg-slate-100 transition-colors"
            >
              <HelpCircle className="w-3.5 h-3.5 text-indigo-600" />
              Explain Score
              {showExplain ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => onViewEvidence(indication.id, indication.indication_name)}
              className="px-3 py-1.5 text-xs font-semibold text-teal-700 bg-teal-50 hover:bg-teal-100 border border-teal-200 rounded-md transition-colors"
            >
              View Evidence Sources
            </button>
          </div>
        </div>

        {/* Expandable Breakdown Drawer */}
        {showBreakdown && (
          <div className="mt-4 pt-4 border-t border-slate-100 bg-slate-50/70 p-4 rounded-lg">
            <EvidenceScoreBreakdown
              clinicalScore={indication.clinical_score}
              patentScore={indication.patent_score}
              literatureScore={indication.literature_score}
              marketScore={indication.market_score}
              overallScore={indication.evidence_score}
            />
          </div>
        )}

        {/* Expandable Explainability Drawer */}
        {showExplain && (
          <div className="mt-4 pt-4 border-t border-slate-100">
            <ExplainabilityPanel
              positiveFactors={indication.positive_factors}
              limitations={indication.limitations}
              explanation={indication.explanation}
            />
          </div>
        )}
      </div>
    </div>
  );
};
