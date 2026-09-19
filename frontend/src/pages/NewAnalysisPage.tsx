import React, { useState, useEffect } from 'react';
import { Pill, HelpCircle, CheckSquare, Square, ArrowRight, Loader2, AlertCircle, CheckCircle2, Sparkles } from 'lucide-react';
import { api } from '../api/client';
import { DrugValidation } from '../types';
import { DisclaimerBanner } from '../components/common/DisclaimerBanner';

interface NewAnalysisPageProps {
  initialDrug?: string;
  onNavigate: (view: string, id?: string) => void;
}

export const NewAnalysisPage: React.FC<NewAnalysisPageProps> = ({ initialDrug = '', onNavigate }) => {
  const [drugName, setDrugName] = useState(initialDrug);
  const [question, setQuestion] = useState('Find potential therapeutic uses beyond its established indications.');
  const [enableClinical, setEnableClinical] = useState(true);
  const [enableLiterature, setEnableLiterature] = useState(true);
  const [enablePatent, setEnablePatent] = useState(true);
  const [enableMarket, setEnableMarket] = useState(true);

  const [validation, setValidation] = useState<DrugValidation | null>(null);
  const [validating, setValidating] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Debounced drug normalization validation
  useEffect(() => {
    if (!drugName.trim() || drugName.trim().length < 2) {
      setValidation(null);
      return;
    }

    const timer = setTimeout(async () => {
      setValidating(true);
      try {
        const res = await api.drugs.validate(drugName.trim());
        setValidation(res);
      } catch (err) {
        // Silently handle
      } finally {
        setValidating(false);
      }
    }, 400);

    return () => clearTimeout(timer);
  }, [drugName]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!drugName.trim()) {
      setError('Please provide a drug name.');
      return;
    }

    setError(null);
    setSubmitting(true);

    try {
      const detail = await api.research.create({
        drug_name: drugName.trim(),
        research_question: question.trim() || undefined,
        enable_clinical: enableClinical,
        enable_literature: enableLiterature,
        enable_patent: enablePatent,
        enable_market: enableMarket
      });

      // Navigate to live analysis screen
      onNavigate('live-analysis', detail.id);
    } catch (err: any) {
      setError(err.message || 'Failed to start research analysis.');
      setSubmitting(false);
    }
  };

  const sampleDrugs = ['Metformin', 'Aspirin', 'Atorvastatin', 'Losartan', 'Rapamycin'];

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
          New Repurposing Investigation
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Deploy specialized agents to investigate an existing pharmaceutical compound.
        </p>
      </div>

      <DisclaimerBanner compact />

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-6">
        {/* Drug Name Input */}
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-700">
              Drug / Compound Name <span className="text-rose-500">*</span>
            </label>
            <div className="flex items-center gap-1 text-[11px] text-slate-400">
              <span>Quick pick:</span>
              {sampleDrugs.map((d) => (
                <button
                  key={d}
                  type="button"
                  onClick={() => setDrugName(d)}
                  className="text-teal-600 hover:text-teal-800 underline font-medium ml-1"
                >
                  {d}
                </button>
              ))}
            </div>
          </div>

          <div className="relative">
            <Pill className="w-5 h-5 text-slate-400 absolute left-3.5 top-3" />
            <input
              type="text"
              required
              value={drugName}
              onChange={(e) => setDrugName(e.target.value)}
              placeholder="e.g. Metformin or Glucophage"
              className="w-full pl-11 pr-10 py-2.5 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent font-medium"
            />
            {validating && (
              <Loader2 className="w-4 h-4 text-teal-600 animate-spin absolute right-3.5 top-3.5" />
            )}
          </div>

          {/* Validation & Normalization Feedback Card */}
          {validation && (
            <div className="mt-3 p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs space-y-1 animate-in fade-in duration-200">
              <div className="flex items-center gap-1.5 text-teal-700 font-semibold">
                <CheckCircle2 className="w-4 h-4 text-teal-600" />
                <span>Canonical Compound: {validation.normalized_name}</span>
                {validation.chembl_id && (
                  <span className="font-mono text-[10px] bg-slate-200/80 px-1.5 py-0.5 rounded text-slate-700">
                    {validation.chembl_id}
                  </span>
                )}
              </div>

              {validation.known_indications.length > 0 && (
                <p className="text-slate-500 text-[11px]">
                  <strong>Established Indications:</strong> {validation.known_indications.join(', ')}
                </p>
              )}

              {validation.canonical_smiles && (
                <p className="font-mono text-[10px] text-slate-400 truncate">
                  SMILES: {validation.canonical_smiles}
                </p>
              )}

              {validation.warnings.length > 0 && (
                <p className="text-amber-700 text-[11px] pt-1">
                  ⚠️ {validation.warnings[0]}
                </p>
              )}
            </div>
          )}
        </div>

        {/* Research Question */}
        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
            Research Question / Hypothesis (Optional)
          </label>
          <textarea
            rows={3}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g. Find therapeutic areas beyond diabetes that have been investigated in clinical trials."
            className="w-full p-3 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
          />
          <p className="text-[11px] text-slate-400 mt-1">
            The Master Agent uses your question to guide indication prioritization and search filtering.
          </p>
        </div>

        {/* Evidence Domains to Activate */}
        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
            Active Multi-Agent Repositories
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <label 
              className={`p-3 rounded-lg border text-xs flex items-center gap-2.5 cursor-pointer transition-colors ${
                enableClinical ? 'bg-teal-50/40 border-teal-300 text-slate-900' : 'bg-slate-50 border-slate-200 text-slate-400'
              }`}
            >
              <input
                type="checkbox"
                checked={enableClinical}
                onChange={(e) => setEnableClinical(e.target.checked)}
                className="rounded text-teal-600 focus:ring-teal-500"
              />
              <div>
                <span className="font-bold block">Clinical Evidence</span>
                <span className="text-[10px] text-slate-500">ClinicalTrials.gov (40% Weight)</span>
              </div>
            </label>

            <label 
              className={`p-3 rounded-lg border text-xs flex items-center gap-2.5 cursor-pointer transition-colors ${
                enableLiterature ? 'bg-blue-50/40 border-blue-300 text-slate-900' : 'bg-slate-50 border-slate-200 text-slate-400'
              }`}
            >
              <input
                type="checkbox"
                checked={enableLiterature}
                onChange={(e) => setEnableLiterature(e.target.checked)}
                className="rounded text-blue-600 focus:ring-blue-500"
              />
              <div>
                <span className="font-bold block">Literature Evidence</span>
                <span className="text-[10px] text-slate-500">NCBI PubMed & Europe PMC (20% Weight)</span>
              </div>
            </label>

            <label 
              className={`p-3 rounded-lg border text-xs flex items-center gap-2.5 cursor-pointer transition-colors ${
                enablePatent ? 'bg-indigo-50/40 border-indigo-300 text-slate-900' : 'bg-slate-50 border-slate-200 text-slate-400'
              }`}
            >
              <input
                type="checkbox"
                checked={enablePatent}
                onChange={(e) => setEnablePatent(e.target.checked)}
                className="rounded text-indigo-600 focus:ring-indigo-500"
              />
              <div>
                <span className="font-bold block">Patent Intelligence</span>
                <span className="text-[10px] text-slate-500">USPTO & PatentsView (30% Weight)</span>
              </div>
            </label>

            <label 
              className={`p-3 rounded-lg border text-xs flex items-center gap-2.5 cursor-pointer transition-colors ${
                enableMarket ? 'bg-amber-50/40 border-amber-300 text-slate-900' : 'bg-slate-50 border-slate-200 text-slate-400'
              }`}
            >
              <input
                type="checkbox"
                checked={enableMarket}
                onChange={(e) => setEnableMarket(e.target.checked)}
                className="rounded text-amber-600 focus:ring-amber-500"
              />
              <div>
                <span className="font-bold block">Market / Regulatory</span>
                <span className="text-[10px] text-slate-500">OpenFDA & Commercial Signals (10% Weight)</span>
              </div>
            </label>
          </div>
        </div>

        {/* Submit Button */}
        <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
          <span className="text-xs text-slate-400">
            Agents run concurrently with async orchestration.
          </span>
          <button
            type="submit"
            disabled={submitting}
            className="px-6 py-3 bg-teal-600 hover:bg-teal-500 text-white font-bold text-sm rounded-lg shadow-md transition-colors flex items-center gap-2 disabled:opacity-50"
          >
            {submitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Spawning Master Agent...
              </>
            ) : (
              <>
                Start MediScan Analysis
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
