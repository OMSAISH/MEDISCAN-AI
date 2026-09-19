import React, { useState, useEffect } from 'react';
import { Stethoscope, BookOpen, ShieldAlert, TrendingUp, ExternalLink, Loader2 } from 'lucide-react';
import { Modal } from '../common/Modal';
import { IndicationEvidenceList } from '../../types';
import { api } from '../../api/client';
import { EvidenceStrengthBadge } from '../common/Badge';

interface EvidenceDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  indicationId: string;
  indicationName: string;
}

export const EvidenceDetailModal: React.FC<EvidenceDetailModalProps> = ({
  isOpen,
  onClose,
  indicationId,
  indicationName
}) => {
  const [activeTab, setActiveTab] = useState<'clinical' | 'literature' | 'patents' | 'market'>('clinical');
  const [data, setData] = useState<IndicationEvidenceList | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && indicationId) {
      setLoading(true);
      setError(null);
      api.evidence.get(indicationId)
        .then((res) => setData(res))
        .catch((err) => setError(err.message || 'Failed to load evidence items.'))
        .finally(() => setLoading(false));
    }
  }, [isOpen, indicationId]);

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={indicationName}
      subtitle={`Granular Multi-Domain Evidence Records (${data?.evidence_score.toFixed(1) || 0} / 100)`}
      maxWidth="4xl"
    >
      {loading ? (
        <div className="py-16 text-center text-slate-400 flex flex-col items-center justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-teal-600 mb-2" />
          <p className="text-sm">Retrieving verified evidence items...</p>
        </div>
      ) : error ? (
        <div className="p-4 bg-rose-50 text-rose-800 rounded-lg text-sm border border-rose-200">
          {error}
        </div>
      ) : data ? (
        <div>
          {/* Tabs */}
          <div className="flex border-b border-slate-200 mb-6 space-x-4">
            <button
              onClick={() => setActiveTab('clinical')}
              className={`pb-3 text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 border-b-2 transition-colors ${
                activeTab === 'clinical'
                  ? 'border-teal-600 text-teal-700'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              <Stethoscope className="w-4 h-4" />
              Clinical Trials ({data.clinical_trials.length})
            </button>

            <button
              onClick={() => setActiveTab('literature')}
              className={`pb-3 text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 border-b-2 transition-colors ${
                activeTab === 'literature'
                  ? 'border-teal-600 text-teal-700'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              <BookOpen className="w-4 h-4" />
              Literature ({data.literature.length})
            </button>

            <button
              onClick={() => setActiveTab('patents')}
              className={`pb-3 text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 border-b-2 transition-colors ${
                activeTab === 'patents'
                  ? 'border-teal-600 text-teal-700'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              <ShieldAlert className="w-4 h-4" />
              Patents ({data.patents.length})
            </button>

            <button
              onClick={() => setActiveTab('market')}
              className={`pb-3 text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 border-b-2 transition-colors ${
                activeTab === 'market'
                  ? 'border-teal-600 text-teal-700'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              <TrendingUp className="w-4 h-4" />
              Market / Regulatory ({data.market_signals.length})
            </button>
          </div>

          {/* Clinical Tab Content */}
          {activeTab === 'clinical' && (
            <div className="space-y-4">
              {data.clinical_trials.length === 0 ? (
                <p className="text-sm text-slate-400 italic py-6 text-center">No clinical trial records for this indication.</p>
              ) : (
                data.clinical_trials.map((trial) => (
                  <div key={trial.id} className="bg-slate-50/70 border border-slate-200 rounded-lg p-4 text-xs">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <span className="font-mono font-bold text-teal-700">{trial.source_id}</span>
                        <h4 className="font-semibold text-slate-900 text-sm mt-1">{trial.title}</h4>
                      </div>
                      <a
                        href={trial.source_url}
                        target="_blank"
                        rel="noreferrer"
                        className="flex items-center gap-1 text-teal-600 hover:text-teal-800 font-medium whitespace-nowrap"
                      >
                        View Source <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-3 pt-3 border-t border-slate-200/60 text-[11px] text-slate-600">
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase">Phase & Status</span>
                        <span className="font-semibold text-slate-800">{trial.evidence_type}</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase">Enrollment</span>
                        <span className="font-semibold text-slate-800">
                          {trial.extracted_facts?.enrollment ? `${trial.extracted_facts.enrollment} participants` : 'Not specified'}
                        </span>
                      </div>
                      <div className="col-span-2">
                        <span className="text-slate-400 block text-[10px] uppercase">Sponsor</span>
                        <span className="font-semibold text-slate-800 truncate block">
                          {trial.extracted_facts?.sponsor || 'Unknown Sponsor'}
                        </span>
                      </div>
                    </div>

                    {trial.extracted_facts?.primary_outcomes?.length > 0 && (
                      <div className="mt-2.5 text-[11px] text-slate-600">
                        <span className="font-semibold text-slate-700">Primary Outcome: </span>
                        {trial.extracted_facts?.primary_outcomes?.[0]}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          )}

          {/* Literature Tab Content */}
          {activeTab === 'literature' && (
            <div className="space-y-4">
              {data.literature.length === 0 ? (
                <p className="text-sm text-slate-400 italic py-6 text-center">No indexed publications for this indication.</p>
              ) : (
                data.literature.map((pub) => (
                  <div key={pub.id} className="bg-slate-50/70 border border-slate-200 rounded-lg p-4 text-xs">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-mono font-bold text-blue-700">{pub.source_id}</span>
                          <span className="px-2 py-0.5 rounded text-[10px] bg-blue-100 text-blue-800 font-medium">
                            {pub.evidence_type}
                          </span>
                        </div>
                        <h4 className="font-semibold text-slate-900 text-sm mt-1">{pub.title}</h4>
                      </div>
                      <a
                        href={pub.source_url}
                        target="_blank"
                        rel="noreferrer"
                        className="flex items-center gap-1 text-blue-600 hover:text-blue-800 font-medium whitespace-nowrap"
                      >
                        PubMed <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                    </div>

                    <div className="mt-2 text-[11px] text-slate-600 flex flex-wrap gap-x-4 gap-y-1">
                      <span><strong>Authors:</strong> {pub.extracted_facts?.authors || 'Unknown'}</span>
                      <span><strong>Journal:</strong> {pub.extracted_facts?.journal || 'Unknown'}</span>
                      {pub.publication_date && <span><strong>Year:</strong> {pub.publication_date}</span>}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {/* Patents Tab Content */}
          {activeTab === 'patents' && (
            <div className="space-y-4">
              {data.patents.length === 0 ? (
                <p className="text-sm text-slate-400 italic py-6 text-center">No patent records linked to this indication.</p>
              ) : (
                data.patents.map((pat) => (
                  <div key={pat.id} className="bg-slate-50/70 border border-slate-200 rounded-lg p-4 text-xs">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <span className="font-mono font-bold text-indigo-700">{pat.source_id}</span>
                        <h4 className="font-semibold text-slate-900 text-sm mt-1">{pat.title}</h4>
                      </div>
                      <a
                        href={pat.source_url}
                        target="_blank"
                        rel="noreferrer"
                        className="flex items-center gap-1 text-indigo-600 hover:text-indigo-800 font-medium whitespace-nowrap"
                      >
                        Google Patents <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                    </div>

                    <div className="mt-2 text-[11px] text-slate-600">
                      <span><strong>Assignee:</strong> {pat.extracted_facts?.assignee || 'Unassigned'}</span>
                      {pat.publication_date && <span className="ml-4"><strong>Filing Date:</strong> {pat.publication_date}</span>}
                    </div>

                    {pat.extracted_facts?.abstract && (
                      <p className="mt-2 text-[11px] text-slate-500 line-clamp-2">
                        {pat.extracted_facts.abstract}
                      </p>
                    )}
                  </div>
                ))
              )}
            </div>
          )}

          {/* Market Tab Content */}
          {activeTab === 'market' && (
            <div className="space-y-4">
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 text-xs">
                <h4 className="font-bold text-slate-900 mb-2">Commercial & Regulatory Exclusivity Landscape</h4>
                <p className="text-slate-600 leading-relaxed">
                  Market scoring assesses active pharmaceutical ingredient (API) generic status, FDA Orange Book exclusivity expiration, 
                  and commercial versus academic trial sponsorship ratios.
                </p>
                <div className="mt-3 p-3 bg-amber-50/80 border border-amber-200 rounded text-amber-900 text-xs">
                  <strong>Notice on Market Projections:</strong> MediScan AI does not fabricate market sizes, CAGR, or ROI estimates. 
                  Commercial data is strictly limited to verifiable public regulatory filings.
                </div>
              </div>
            </div>
          )}
        </div>
      ) : null}
    </Modal>
  );
};
