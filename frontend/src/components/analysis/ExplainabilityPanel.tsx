import React from 'react';
import { PlusCircle, MinusCircle, Info } from 'lucide-react';

interface ExplainabilityPanelProps {
  positiveFactors?: string[];
  limitations?: string[];
  explanation?: string;
}

export const ExplainabilityPanel: React.FC<ExplainabilityPanelProps> = ({
  positiveFactors = [],
  limitations = [],
  explanation
}) => {
  return (
    <div className="space-y-4">
      {explanation && (
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-3.5 text-xs text-slate-700 flex items-start gap-2.5">
          <Info className="w-4 h-4 text-teal-600 flex-shrink-0 mt-0.5" />
          <p className="leading-relaxed">{explanation}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Positive Drivers */}
        <div className="bg-emerald-50/50 border border-emerald-200/80 rounded-lg p-3.5">
          <h5 className="text-xs font-bold text-emerald-900 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
            <PlusCircle className="w-3.5 h-3.5 text-emerald-600" />
            Positive Evidence Drivers
          </h5>
          {positiveFactors.length > 0 ? (
            <ul className="space-y-2 text-xs text-emerald-800">
              {positiveFactors.map((f, i) => (
                <li key={i} className="flex items-start gap-1.5">
                  <span className="text-emerald-500 font-bold">+</span>
                  <span>{f}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-xs text-slate-400 italic">No strong positive drivers detected.</p>
          )}
        </div>

        {/* Limitations & Gaps */}
        <div className="bg-amber-50/50 border border-amber-200/80 rounded-lg p-3.5">
          <h5 className="text-xs font-bold text-amber-900 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
            <MinusCircle className="w-3.5 h-3.5 text-amber-600" />
            Limitations & Evidence Gaps
          </h5>
          {limitations.length > 0 ? (
            <ul className="space-y-2 text-xs text-amber-800">
              {limitations.map((l, i) => (
                <li key={i} className="flex items-start gap-1.5">
                  <span className="text-amber-500 font-bold">−</span>
                  <span>{l}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-xs text-slate-400 italic">No major limiting factors flagged.</p>
          )}
        </div>
      </div>
    </div>
  );
};
