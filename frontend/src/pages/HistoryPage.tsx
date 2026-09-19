import React, { useState, useEffect } from 'react';
import { History, Search, ArrowLeft, Loader2, Trash2, ArrowRight } from 'lucide-react';
import { api } from '../api/client';
import { ResearchSummary } from '../types';
import { RecentResearchTable } from '../components/dashboard/RecentResearchTable';
import { DisclaimerBanner } from '../components/common/DisclaimerBanner';

interface HistoryPageProps {
  onNavigate: (view: string, id?: string) => void;
}

export const HistoryPage: React.FC<HistoryPageProps> = ({ onNavigate }) => {
  const [queries, setQueries] = useState<ResearchSummary[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      const data = await api.research.history(100);
      setQueries(data);
    } catch (err) {
      console.error('Failed to load history', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleDelete = async (id: string) => {
    if (window.confirm('Delete this research record?')) {
      try {
        await api.research.delete(id);
        setQueries((prev) => prev.filter((q) => q.id !== id));
      } catch (err) {
        alert('Failed to delete query');
      }
    }
  };

  const filteredQueries = queries.filter((q) => {
    const term = search.toLowerCase();
    return (
      q.drug_name.toLowerCase().includes(term) ||
      (q.normalized_drug_name && q.normalized_drug_name.toLowerCase().includes(term)) ||
      (q.research_question && q.research_question.toLowerCase().includes(term))
    );
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <History className="w-6 h-6 text-teal-600" />
            Research History & Archives
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Access and review previously synthesized drug repurposing investigations.
          </p>
        </div>

        {/* Search Bar */}
        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by drug or question..."
            className="w-full pl-9 pr-3 py-2 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
          />
        </div>
      </div>

      <DisclaimerBanner compact />

      {loading ? (
        <div className="py-20 text-center text-slate-400 flex flex-col items-center justify-center">
          <Loader2 className="w-6 h-6 animate-spin text-teal-600 mb-2" />
          <p className="text-xs font-medium">Loading archives...</p>
        </div>
      ) : (
        <RecentResearchTable
          queries={filteredQueries}
          onSelectQuery={(id) => onNavigate('results', id)}
          onDeleteQuery={handleDelete}
        />
      )}
    </div>
  );
};
