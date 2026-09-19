import React, { useState, useEffect } from 'react';
import { Pill, Download, Layers, Stethoscope, BookOpen, ShieldAlert, ArrowLeft, Loader2, FileText, CheckCircle2 } from 'lucide-react';
import { api } from '../api/client';
import { ResearchDetail, ReportFormat } from '../types';
import { IndicationCard } from '../components/analysis/IndicationCard';
import { EvidenceDetailModal } from '../components/analysis/EvidenceDetailModal';
import { DisclaimerBanner } from '../components/common/DisclaimerBanner';
import { Modal } from '../components/common/Modal';

interface ResultsPageProps {
  queryId: string;
  onNavigate: (view: string, id?: string) => void;
}

export const ResultsPage: React.FC<ResultsPageProps> = ({ queryId, onNavigate }) => {
  const [detail, setDetail] = useState<ResearchDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Evidence Modal State
  const [selectedIndicationId, setSelectedIndicationId] = useState<string | null>(null);
  const [selectedIndicationName, setSelectedIndicationName] = useState<string>('');

  // Report Generation Modal State
  const [showReportModal, setShowReportModal] = useState(false);
  const [selectedFormat, setSelectedFormat] = useState<ReportFormat>('PDF');
  const [generatingReport, setGeneratingReport] = useState(false);
  const [downloadSuccess, setDownloadSuccess] = useState(false);

  useEffect(() => {
    api.research.get(queryId)
      .then((res) => setDetail(res))
      .catch((err) => setError(err.message || 'Failed to load research results.'))
      .finally(() => setLoading(false));
  }, [queryId]);

  const handleOpenEvidence = (id: string, name: string) => {
    setSelectedIndicationId(id);
    setSelectedIndicationName(name);
  };

  const handleGenerateReport = async () => {
    setGeneratingReport(true);
    setDownloadSuccess(false);
    try {
      const report = await api.reports.generate(queryId, selectedFormat);
      // Trigger file download
      window.open(api.reports.downloadUrl(report.id), '_blank');
      setDownloadSuccess(true);
      setTimeout(() => setShowReportModal(false), 2000);
    } catch (err: any) {
      alert(err.message || 'Report generation failed');
    } finally {
      setGeneratingReport(false);
    }
  };

  if (loading) {
    return (
      <div className="py-24 text-center text-slate-400 flex flex-col items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-teal-600 mb-3" />
        <p className="text-sm font-medium text-slate-600">Synthesizing research dossier...</p>
      </div>
    );
  }

  if (error || !detail) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="p-6 bg-rose-50 border border-rose-200 text-rose-900 rounded-xl">
          <h3 className="font-bold text-base">Error Loading Results</h3>
          <p className="text-sm mt-1">{error || 'Analysis record could not be found.'}</p>
          <button
            onClick={() => onNavigate('dashboard')}
            className="mt-4 px-4 py-2 bg-slate-900 text-white rounded-lg text-xs font-semibold"
          >
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }

  // Summary counts
  const totalTrials = detail.indications.reduce((acc, i) => acc + i.clinical_trial_count, 0);
  const totalPubs = detail.indications.reduce((acc, i) => acc + i.literature_count, 0);
  const totalPatents = detail.indications.reduce((acc, i) => acc + i.patent_count, 0);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Navigation & Header */}
      <div>
        <button
          onClick={() => onNavigate('dashboard')}
          className="text-xs font-semibold text-slate-500 hover:text-slate-800 flex items-center gap-1 mb-3 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Dashboard
        </button>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-teal-600 font-mono">
                Repurposing Intelligence Dossier
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] bg-slate-100 font-mono text-slate-600">
                {detail.execution_time_ms ? `${detail.execution_time_ms} ms` : 'Complete'}
              </span>
            </div>
            <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight mt-1">
              {detail.normalized_drug_name || detail.drug_name}
            </h1>
            {detail.research_question && (
              <p className="text-xs text-slate-500 mt-1 max-w-2xl">
                <strong>Query:</strong> {detail.research_question}
              </p>
            )}
          </div>

          <button
            onClick={() => setShowReportModal(true)}
            className="px-5 py-2.5 bg-teal-600 hover:bg-teal-500 text-white rounded-lg font-bold text-xs shadow-sm transition-colors flex items-center gap-2 self-start sm:self-auto"
          >
            <Download className="w-4 h-4" />
            Generate Research Report
          </button>
        </div>
      </div>

      <DisclaimerBanner compact />

      {/* Summary Metrics Banner */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <div className="flex items-center gap-2 text-slate-500 text-xs font-semibold uppercase">
            <Pill className="w-4 h-4 text-teal-600" /> Indications
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-1">{detail.indications.length}</p>
          <span className="text-[11px] text-slate-400">Investigated clusters</span>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <div className="flex items-center gap-2 text-slate-500 text-xs font-semibold uppercase">
            <Stethoscope className="w-4 h-4 text-teal-600" /> Clinical Trials
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-1">{totalTrials}</p>
          <span className="text-[11px] text-slate-400">ClinicalTrials.gov records</span>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <div className="flex items-center gap-2 text-slate-500 text-xs font-semibold uppercase">
            <BookOpen className="w-4 h-4 text-blue-600" /> Publications
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-1">{totalPubs}</p>
          <span className="text-[11px] text-slate-400">Peer-reviewed papers</span>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <div className="flex items-center gap-2 text-slate-500 text-xs font-semibold uppercase">
            <ShieldAlert className="w-4 h-4 text-indigo-600" /> Patent Records
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-1">{totalPatents}</p>
          <span className="text-[11px] text-slate-400">USPTO & PatentsView</span>
        </div>
      </div>

      {/* Executive Summary */}
      {detail.executive_summary && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm space-y-3">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-900 flex items-center gap-2">
            <FileText className="w-4 h-4 text-teal-600" />
            Executive Research Synthesis
          </h3>
          <div className="text-xs text-slate-700 leading-relaxed space-y-2 whitespace-pre-line">
            {detail.executive_summary}
          </div>
        </div>
      )}

      {/* Discovered Indications Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-slate-900">
            Discovered Therapeutic Indications ({detail.indications.length})
          </h2>
          <span className="text-xs text-slate-500">Sorted by Evidence Score</span>
        </div>

        <div className="space-y-4">
          {detail.indications.map((ind) => (
            <IndicationCard
              key={ind.id}
              indication={ind}
              onViewEvidence={handleOpenEvidence}
            />
          ))}
        </div>
      </div>

      {/* Granular Evidence Modal */}
      {selectedIndicationId && (
        <EvidenceDetailModal
          isOpen={!!selectedIndicationId}
          onClose={() => setSelectedIndicationId(null)}
          indicationId={selectedIndicationId}
          indicationName={selectedIndicationName}
        />
      )}

      {/* Report Generation Modal */}
      <Modal
        isOpen={showReportModal}
        onClose={() => setShowReportModal(false)}
        title="Export Pharmaceutical Research Dossier"
        subtitle={`Generate verified report for ${detail.normalized_drug_name || detail.drug_name}`}
        maxWidth="md"
      >
        <div className="space-y-4">
          <p className="text-xs text-slate-600">
            Select an export format. PDF reports contain publication-quality executive summaries, indication tables, and methodology disclosures.
          </p>

          <div className="grid grid-cols-2 gap-2">
            {(['PDF', 'HTML', 'JSON', 'CSV'] as ReportFormat[]).map((fmt) => (
              <button
                key={fmt}
                type="button"
                onClick={() => setSelectedFormat(fmt)}
                className={`p-3 rounded-lg border text-center text-xs font-bold transition-colors ${
                  selectedFormat === fmt
                    ? 'border-teal-600 bg-teal-50 text-teal-900 ring-2 ring-teal-500'
                    : 'border-slate-200 hover:bg-slate-50 text-slate-700'
                }`}
              >
                {fmt} Format
              </button>
            ))}
          </div>

          {downloadSuccess && (
            <div className="p-3 bg-emerald-50 text-emerald-800 rounded-lg text-xs flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Report generated! Download opened in a new tab.</span>
            </div>
          )}

          <div className="pt-3 border-t border-slate-100 flex items-center justify-end gap-2">
            <button
              onClick={() => setShowReportModal(false)}
              className="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-800"
            >
              Cancel
            </button>
            <button
              onClick={handleGenerateReport}
              disabled={generatingReport}
              className="px-5 py-2 bg-teal-600 hover:bg-teal-500 text-white rounded-lg text-xs font-bold shadow transition-colors flex items-center gap-2 disabled:opacity-50"
            >
              {generatingReport ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
              Generate & Download
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
