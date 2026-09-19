import React, { useState, useEffect } from 'react';
import { Shield, Activity, Database, Server, Clock, Users, Layers, AlertCircle, Loader2 } from 'lucide-react';
import { api } from '../api/client';
import { AdminOverview, AuditLogItem } from '../types';

export const AdminPage: React.FC = () => {
  const [overview, setOverview] = useState<AdminOverview | null>(null);
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.admin.overview(), api.admin.auditLogs(30)])
      .then(([ov, lg]) => {
        setOverview(ov);
        setLogs(lg);
      })
      .catch((err) => setError(err.message || 'Failed to load admin telemetry.'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="py-24 text-center text-slate-400 flex flex-col items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-teal-600 mb-2" />
        <p className="text-xs font-semibold">Loading system telemetry & audit logs...</p>
      </div>
    );
  }

  if (error || !overview) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-900 rounded-xl text-xs">
          {error || 'Unauthorized or telemetry unavailable.'}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-teal-600" />
            <span className="text-xs font-bold uppercase tracking-wider text-teal-600 font-mono">
              System Administration
            </span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight mt-1">
            Platform Health & Audit Telemetry
          </h1>
        </div>

        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
          <span className="text-xs font-mono text-slate-600">
            System {overview.system_health.status.toUpperCase()} (v{overview.system_health.version})
          </span>
        </div>
      </div>

      {/* Top Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <span className="text-slate-400 text-xs font-semibold uppercase flex items-center gap-1.5">
            <Users className="w-4 h-4 text-teal-600" /> Registered Users
          </span>
          <p className="text-2xl font-bold text-slate-900 mt-1">{overview.total_users}</p>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <span className="text-slate-400 text-xs font-semibold uppercase flex items-center gap-1.5">
            <Activity className="w-4 h-4 text-blue-600" /> Total Analyses
          </span>
          <p className="text-2xl font-bold text-slate-900 mt-1">{overview.total_analyses}</p>
          <span className="text-[11px] text-emerald-600">{overview.completed_analyses} completed</span>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <span className="text-slate-400 text-xs font-semibold uppercase flex items-center gap-1.5">
            <Database className="w-4 h-4 text-indigo-600" /> Evidence Records
          </span>
          <p className="text-2xl font-bold text-slate-900 mt-1">{overview.total_evidence_items}</p>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <span className="text-slate-400 text-xs font-semibold uppercase flex items-center gap-1.5">
            <Clock className="w-4 h-4 text-amber-600" /> System Uptime
          </span>
          <p className="text-2xl font-bold text-slate-900 mt-1">
            {(overview.system_health.uptime_seconds / 60).toFixed(1)}m
          </p>
        </div>
      </div>

      {/* Agent Metrics Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden p-6 space-y-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-900 flex items-center gap-2">
          <Server className="w-4 h-4 text-teal-600" />
          Specialized Agent Execution Performance
        </h3>

        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-xs divide-y divide-slate-200">
            <thead className="bg-slate-50 text-slate-500 uppercase font-semibold">
              <tr>
                <th className="px-4 py-3">Agent Name</th>
                <th className="px-4 py-3 text-center">Total Invocations</th>
                <th className="px-4 py-3 text-center">Success Rate</th>
                <th className="px-4 py-3 text-right">Avg Latency (ms)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {overview.agent_metrics.map((m) => {
                const rate = m.total_runs > 0 ? ((m.successful_runs / m.total_runs) * 100).toFixed(0) : '100';
                return (
                  <tr key={m.agent_name} className="hover:bg-slate-50">
                    <td className="px-4 py-3 font-semibold text-slate-900">{m.agent_name}</td>
                    <td className="px-4 py-3 text-center">{m.total_runs}</td>
                    <td className="px-4 py-3 text-center">
                      <span className="px-2 py-0.5 rounded-full font-bold bg-emerald-50 text-emerald-700">
                        {rate}%
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right font-mono">{m.avg_execution_time_ms} ms</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Audit Logs Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-900 flex items-center gap-2">
            <Shield className="w-4 h-4 text-teal-600" />
            Security & Audit Trail
          </h3>
          <span className="text-[11px] text-slate-400 font-mono">Immutable User Actions</span>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-xs divide-y divide-slate-200">
            <thead className="bg-slate-50 text-slate-500 uppercase font-semibold">
              <tr>
                <th className="px-4 py-3">Timestamp</th>
                <th className="px-4 py-3">User</th>
                <th className="px-4 py-3">Action</th>
                <th className="px-4 py-3">Resource</th>
                <th className="px-4 py-3">IP Address</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700 font-mono text-[11px]">
              {logs.map((l) => (
                <tr key={l.id} className="hover:bg-slate-50">
                  <td className="px-4 py-2.5 text-slate-500 whitespace-nowrap">
                    {new Date(l.created_at).toLocaleString()}
                  </td>
                  <td className="px-4 py-2.5 text-slate-900">{l.user_email || 'Anonymous'}</td>
                  <td className="px-4 py-2.5">
                    <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-800 font-bold">
                      {l.action}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-slate-600">{l.resource_type}</td>
                  <td className="px-4 py-2.5 text-slate-400">{l.ip_address || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
