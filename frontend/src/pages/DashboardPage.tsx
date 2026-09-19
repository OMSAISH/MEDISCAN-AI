import React, { useState, useEffect } from 'react';
import { Pill, Activity, CheckCircle2, Layers, Search, PlusCircle, ArrowRight, Loader2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { ResearchSummary } from '../types';
import { api } from '../api/client';
import { StatsCard } from '../components/dashboard/StatsCard';
import { RecentResearchTable } from '../components/dashboard/RecentResearchTable';
import { DisclaimerBanner } from '../components/common/DisclaimerBanner';

interface DashboardPageProps {
  onNavigate: (view: string, id?: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate }) => {
  const { user } = useAuth();
  const [queries, setQueries] = useState<ResearchSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [quickDrug, setQuickDrug] = useState('');

  const loadHistory = async () => {
    try {
      const data = await api.research.history();
      setQueries(data);
    } catch (err) {
      console.error('Failed to load history', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleQuickSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (quickDrug.trim()) {
      onNavigate(`new-analysis:${encodeURIComponent(quickDrug.trim())}`);
    }
  };

  const handleDeleteQuery = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this research analysis?')) {
      try {
        await api.research.delete(id);
        setQueries((prev) => prev.filter((q) => q.id !== id));
      } catch (err) {
        alert('Failed to delete analysis');
      }
    }
  };

  // Compute stats
  const totalAnalyses = queries.length;
  const completedAnalyses = queries.filter((q) => q.status === 'COMPLETED' || q.status === 'PARTIAL_FAILURE').length;
  const totalIndications = queries.reduce((acc, q) => acc + q.indication_count, 0);
  const totalEvidenceItems = queries.reduce(
    (acc, q) => acc + q.clinical_trial_count + q.literature_count + q.patent_count,
    0
  );

  return (
    <div className="space-y-8 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header & Welcome */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Research Intelligence Dashboard
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Welcome back, {user?.full_name}. Systematic multi-agent drug repurposing workspace.
          </p>
        </div>
        <button
          onClick={() => onNavigate('new-analysis')}
          className="px-4 py-2 bg-teal-600 hover:bg-teal-500 text-white rounded-lg font-bold text-sm shadow-sm transition-colors flex items-center gap-2 self-start sm:self-auto"
        >
          <PlusCircle className="w-4 h-4" />
          New Investigation
        </button>
      </div>

      <DisclaimerBanner compact />

      {/* Quick Search Card */}
      <div className="bg-slate-900 text-white rounded-2xl p-6 sm:p-8 shadow-xl border border-slate-800">
        <div className="max-w-2xl space-y-4">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-teal-500/20 text-teal-400 text-xs font-semibold uppercase tracking-wider">
            <Search className="w-3.5 h-3.5" />
            Quick Investigation
          </div>
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight">
            Scan an Existing Drug Across Clinical & Literature Space
          </h2>
          <p className="text-xs text-slate-300 leading-relaxed">
            Enter a generic or brand-name compound to validate chemical identity and initiate multi-agent evidence discovery.
          </p>

          <form onSubmit={handleQuickSubmit} className="flex flex-col sm:flex-row gap-2 pt-2">
            <div className="relative flex-1">
              <Pill className="w-5 h-5 text-slate-400 absolute left-3.5 top-3" />
              <input
                type="text"
                value={quickDrug}
                onChange={(e) => setQuickDrug(e.target.value)}
                placeholder="e.g. Metformin, Aspirin, Atorvastatin, Losartan..."
                className="w-full pl-11 pr-4 py-2.5 text-sm bg-slate-800/90 border border-slate-700 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-teal-400"
              />
            </div>
            <button
              type="submit"
              className="px-6 py-2.5 bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-sm rounded-lg transition-colors flex items-center justify-center gap-1.5 shadow"
            >
              Investigate <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>

      {/* Stats Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Total Analyses"
          value={totalAnalyses}
          subtitle="Lifetime queries launched"
          icon={Activity}
          colorClass="text-teal-600 bg-teal-50 border-teal-100"
        />
        <StatsCard
          title="Completed Scans"
          value={completedAnalyses}
          subtitle="Fully aggregated pipelines"
          icon={CheckCircle2}
          colorClass="text-emerald-600 bg-emerald-50 border-emerald-100"
        />
        <StatsCard
          title="Discovered Indications"
          value={totalIndications}
          subtitle="Hypotheses identified"
          icon={Pill}
          colorClass="text-blue-600 bg-blue-50 border-blue-100"
        />
        <StatsCard
          title="Synthesized Records"
          value={totalEvidenceItems}
          subtitle="Trials, papers & patents"
          icon={Layers}
          colorClass="text-indigo-600 bg-indigo-50 border-indigo-100"
        />
      </div>

      {/* Recent Research Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-slate-900">Recent Investigations</h3>
          <button
            onClick={() => onNavigate('history')}
            className="text-xs font-semibold text-teal-600 hover:text-teal-700"
          >
            View All History →
          </button>
        </div>

        {loading ? (
          <div className="py-12 text-center text-slate-400 flex flex-col items-center justify-center">
            <Loader2 className="w-6 h-6 animate-spin text-teal-600 mb-2" />
            <p className="text-xs">Loading research history...</p>
          </div>
        ) : (
          <RecentResearchTable
            queries={queries.slice(0, 5)}
            onSelectQuery={(id) => onNavigate('results', id)}
            onDeleteQuery={handleDeleteQuery}
          />
        )}
      </div>
    </div>
  );
};
