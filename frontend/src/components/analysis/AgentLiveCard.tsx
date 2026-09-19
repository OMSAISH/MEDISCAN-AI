import React from 'react';
import { Stethoscope, BookOpen, ShieldAlert, TrendingUp, CheckCircle, Clock, AlertCircle, Loader2 } from 'lucide-react';
import { AgentStatus } from '../../types';

interface AgentLiveCardProps {
  name: string;
  type: 'clinical' | 'literature' | 'patent' | 'market';
  status: AgentStatus;
  itemsFound: number;
  executionTimeMs?: number;
  currentOperation?: string;
  sourceRepo: string;
}

export const AgentLiveCard: React.FC<AgentLiveCardProps> = ({
  name,
  type,
  status,
  itemsFound,
  executionTimeMs,
  currentOperation,
  sourceRepo
}) => {
  const iconMap = {
    clinical: Stethoscope,
    literature: BookOpen,
    patent: ShieldAlert,
    market: TrendingUp
  };
  const Icon = iconMap[type];

  const statusConfig = {
    QUEUED: {
      color: 'bg-slate-50 border-slate-200 text-slate-500',
      badge: 'bg-slate-100 text-slate-600',
      icon: Clock,
      label: 'Queued'
    },
    RUNNING: {
      color: 'bg-teal-50/50 border-teal-300 text-teal-900 shadow-sm',
      badge: 'bg-teal-100 text-teal-800 animate-pulse',
      icon: Loader2,
      label: 'Analyzing...'
    },
    COMPLETED: {
      color: 'bg-white border-emerald-200 text-slate-900 shadow-sm',
      badge: 'bg-emerald-100 text-emerald-800',
      icon: CheckCircle,
      label: 'Completed'
    },
    FAILED: {
      color: 'bg-rose-50/50 border-rose-200 text-rose-900',
      badge: 'bg-rose-100 text-rose-800',
      icon: AlertCircle,
      label: 'Failed'
    }
  }[status];

  const StatusIcon = statusConfig.icon;

  return (
    <div className={`rounded-xl border p-5 transition-all duration-300 ${statusConfig.color}`}>
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className={`p-2.5 rounded-lg ${status === 'RUNNING' ? 'bg-teal-600 text-white animate-bounce' : 'bg-slate-100 text-slate-700'}`}>
            <Icon className="w-5 h-5" />
          </div>
          <div>
            <h4 className="font-bold text-sm text-slate-900">{name}</h4>
            <p className="text-[11px] text-slate-500 font-mono mt-0.5">{sourceRepo}</p>
          </div>
        </div>
        <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold ${statusConfig.badge}`}>
          <StatusIcon className={`w-3.5 h-3.5 ${status === 'RUNNING' ? 'animate-spin' : ''}`} />
          {statusConfig.label}
        </span>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-100 grid grid-cols-2 gap-2 text-xs">
        <div>
          <span className="text-slate-400 block text-[10px] uppercase">Records Discovered</span>
          <span className="font-bold text-base text-slate-900">{itemsFound}</span>
        </div>
        <div className="text-right">
          <span className="text-slate-400 block text-[10px] uppercase">Execution Latency</span>
          <span className="font-mono text-slate-700">
            {executionTimeMs !== undefined ? `${executionTimeMs} ms` : '—'}
          </span>
        </div>
      </div>

      {currentOperation && (
        <div className="mt-3 text-[11px] text-slate-600 bg-slate-100/70 rounded p-2 border border-slate-200/50 truncate">
          {currentOperation}
        </div>
      )}
    </div>
  );
};
