import React from 'react';
import { AlertTriangle } from 'lucide-react';

export const DisclaimerBanner: React.FC<{ compact?: boolean }> = ({ compact = false }) => {
  if (compact) {
    return (
      <div className="bg-amber-50/70 border border-amber-200/80 rounded-md p-2.5 text-xs text-amber-900 flex items-center gap-2">
        <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0" />
        <span>
          <strong>Research Intelligence Tool:</strong> Outputs are for scientific hypothesis generation. Not medical advice or clinical approval.
        </span>
      </div>
    );
  }

  return (
    <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm text-amber-900 flex items-start gap-3 shadow-sm">
      <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
      <div>
        <h4 className="font-semibold text-amber-950 text-xs tracking-wider uppercase">
          Pharmaceutical Research & Regulatory Disclaimer
        </h4>
        <p className="mt-1 text-xs text-amber-800 leading-relaxed">
          MediScan AI is an evidence-driven research intelligence and hypothesis-generation platform. Its outputs do not constitute 
          medical advice, clinical diagnosis, treatment recommendations, or regulatory efficacy determinations. All findings represent 
          empirical evidence synthesized from public clinical trial registries, scientific literature, patent offices, and regulatory records.
        </p>
      </div>
    </div>
  );
};
