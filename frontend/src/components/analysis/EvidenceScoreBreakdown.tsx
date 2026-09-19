import React from 'react';

interface EvidenceScoreBreakdownProps {
  clinicalScore: number;
  patentScore: number;
  literatureScore: number;
  marketScore: number;
  overallScore: number;
}

export const EvidenceScoreBreakdown: React.FC<EvidenceScoreBreakdownProps> = ({
  clinicalScore,
  patentScore,
  literatureScore,
  marketScore,
  overallScore
}) => {
  const components = [
    { label: 'Clinical Trials', weight: '40%', score: clinicalScore, color: 'bg-teal-500' },
    { label: 'Patent Landscape', weight: '30%', score: patentScore, color: 'bg-indigo-500' },
    { label: 'Scientific Literature', weight: '20%', score: literatureScore, color: 'bg-sky-500' },
    { label: 'Market / Regulatory', weight: '10%', score: marketScore, color: 'bg-amber-500' },
  ];

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between border-b border-slate-100 pb-2">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Component Scoring Weights</span>
        <span className="text-sm font-bold text-teal-700">
          Composite: {overallScore.toFixed(1)} / 100
        </span>
      </div>

      <div className="space-y-2.5">
        {components.map((c) => (
          <div key={c.label} className="text-xs">
            <div className="flex justify-between items-center mb-1">
              <span className="text-slate-700 font-medium">
                {c.label} <span className="text-slate-400 text-[10px]">({c.weight})</span>
              </span>
              <span className="font-mono font-semibold text-slate-800">{c.score.toFixed(1)}</span>
            </div>
            <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${c.color}`}
                style={{ width: `${Math.min(100, Math.max(0, c.score))}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>

      <p className="text-[10px] text-slate-400 italic pt-1">
        Weighted formula: 0.40 × Clinical + 0.30 × Patent + 0.20 × Literature + 0.10 × Market
      </p>
    </div>
  );
};
