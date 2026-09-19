import React from 'react';
import { Pill, ArrowRight, Clock, FileText, Trash2 } from 'lucide-react';
import { ResearchSummary } from '../../types';
import { StatusBadge } from '../common/Badge';

interface RecentResearchTableProps {
  queries: ResearchSummary[];
  onSelectQuery: (id: string) => void;
  onDeleteQuery?: (id: string) => void;
}

export const RecentResearchTable: React.FC<RecentResearchTableProps> = ({
  queries,
  onSelectQuery,
  onDeleteQuery
}) => {
  if (queries.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
        <Pill className="w-10 h-10 text-slate-300 mx-auto mb-3" />
        <h3 className="text-base font-semibold text-slate-800">No Research Analyses Yet</h3>
        <p className="text-sm text-slate-500 mt-1 max-w-md mx-auto">
          Begin your first drug repurposing investigation by entering an existing compound.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
          <thead className="bg-slate-50 text-slate-600 font-semibold text-xs uppercase tracking-wider">
            <tr>
              <th scope="col" className="px-6 py-3.5">Investigated Drug</th>
              <th scope="col" className="px-6 py-3.5">Research Question</th>
              <th scope="col" className="px-6 py-3.5">Status</th>
              <th scope="col" className="px-6 py-3.5 text-center">Indications</th>
              <th scope="col" className="px-6 py-3.5 text-center">Evidence Volume</th>
              <th scope="col" className="px-6 py-3.5">Date</th>
              <th scope="col" className="px-6 py-3.5 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-slate-700">
            {queries.map((q) => (
              <tr 
                key={q.id} 
                className="hover:bg-slate-50/80 transition-colors cursor-pointer group"
                onClick={() => onSelectQuery(q.id)}
              >
                <td className="px-6 py-4 font-semibold text-slate-900 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-teal-500"></span>
                  {q.normalized_drug_name || q.drug_name}
                </td>
                <td className="px-6 py-4 max-w-xs truncate text-slate-500 text-xs">
                  {q.research_question || 'Comprehensive repurposing scan'}
                </td>
                <td className="px-6 py-4">
                  <StatusBadge status={q.status} />
                </td>
                <td className="px-6 py-4 text-center font-semibold text-slate-900">
                  {q.indication_count}
                </td>
                <td className="px-6 py-4 text-center text-xs text-slate-500">
                  <span className="inline-flex gap-1.5 font-mono">
                    <span title="Clinical Trials" className="text-teal-700 bg-teal-50 px-1.5 py-0.5 rounded">
                      {q.clinical_trial_count} CT
                    </span>
                    <span title="Publications" className="text-blue-700 bg-blue-50 px-1.5 py-0.5 rounded">
                      {q.literature_count} Lit
                    </span>
                    <span title="Patents" className="text-purple-700 bg-purple-50 px-1.5 py-0.5 rounded">
                      {q.patent_count} Pat
                    </span>
                  </span>
                </td>
                <td className="px-6 py-4 text-xs text-slate-500 whitespace-nowrap">
                  <div className="flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-slate-400" />
                    {new Date(q.created_at).toLocaleDateString()}
                  </div>
                </td>
                <td className="px-6 py-4 text-right whitespace-nowrap">
                  <div className="flex items-center justify-end gap-2" onClick={(e) => e.stopPropagation()}>
                    <button
                      onClick={() => onSelectQuery(q.id)}
                      className="px-2.5 py-1 text-xs font-medium text-teal-700 bg-teal-50 hover:bg-teal-100 rounded border border-teal-200 transition-colors flex items-center gap-1"
                    >
                      View <ArrowRight className="w-3 h-3" />
                    </button>
                    {onDeleteQuery && (
                      <button
                        onClick={() => onDeleteQuery(q.id)}
                        className="p-1 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded transition-colors"
                        title="Delete analysis"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
