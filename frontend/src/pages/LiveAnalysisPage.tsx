import React, { useState, useEffect } from 'react';
import { Cpu, CheckCircle2, ArrowRight, Loader2, AlertCircle, RefreshCw, Layers } from 'lucide-react';
import { api } from '../api/client';
import { AgentStatus, QueryStatus } from '../types';
import { AgentLiveCard } from '../components/analysis/AgentLiveCard';
import { DisclaimerBanner } from '../components/common/DisclaimerBanner';

interface LiveAnalysisPageProps {
  queryId: string;
  onNavigate: (view: string, id?: string) => void;
}

interface LogEvent {
  time: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
}

export const LiveAnalysisPage: React.FC<LiveAnalysisPageProps> = ({ queryId, onNavigate }) => {
  const [drugName, setDrugName] = useState<string>('Compound');
  const [queryStatus, setQueryStatus] = useState<QueryStatus>('RUNNING');
  const [logs, setLogs] = useState<LogEvent[]>([
    { time: new Date().toLocaleTimeString(), message: 'Research task received by Master Agent.', type: 'info' },
    { time: new Date().toLocaleTimeString(), message: 'Decomposing task and initializing specialized agents...', type: 'info' }
  ]);

  const [clinicalStatus, setClinicalStatus] = useState<AgentStatus>('RUNNING');
  const [clinicalCount, setClinicalCount] = useState<number>(0);
  const [clinicalTime, setClinicalTime] = useState<number | undefined>();

  const [literatureStatus, setLiteratureStatus] = useState<AgentStatus>('RUNNING');
  const [literatureCount, setLiteratureCount] = useState<number>(0);
  const [literatureTime, setLiteratureTime] = useState<number | undefined>();

  const [patentStatus, setPatentStatus] = useState<AgentStatus>('RUNNING');
  const [patentCount, setPatentCount] = useState<number>(0);
  const [patentTime, setPatentTime] = useState<number | undefined>();

  const [marketStatus, setMarketStatus] = useState<AgentStatus>('RUNNING');
  const [marketCount, setMarketCount] = useState<number>(0);
  const [marketTime, setMarketTime] = useState<number | undefined>();

  const [indicationsCount, setIndicationsCount] = useState<number>(0);

  useEffect(() => {
    let isMounted = true;

    // Connect to SSE stream
    const eventSource = api.research.getEventSource(queryId);

    eventSource.addEventListener('query_started', (e: any) => {
      const data = JSON.parse(e.data);
      if (data.drug_name) setDrugName(data.drug_name);
      addLog(`Master Agent: ${data.message}`, 'info');
    });

    eventSource.addEventListener('agents_launched', (e: any) => {
      const data = JSON.parse(e.data);
      addLog(`Master Agent: ${data.message}`, 'info');
    });

    eventSource.addEventListener('agent_started', (e: any) => {
      const data = JSON.parse(e.data);
      addLog(`${data.agent_name}: ${data.message}`, 'info');
    });

    eventSource.addEventListener('agent_completed', (e: any) => {
      const data = JSON.parse(e.data);
      addLog(`✓ ${data.agent_name}: Retrieved ${data.items_found} records in ${data.execution_time_ms}ms`, 'success');

      if (data.agent_name.includes('Clinical')) {
        setClinicalStatus('COMPLETED');
        setClinicalCount(data.items_found);
        setClinicalTime(data.execution_time_ms);
      } else if (data.agent_name.includes('Literature')) {
        setLiteratureStatus('COMPLETED');
        setLiteratureCount(data.items_found);
        setLiteratureTime(data.execution_time_ms);
      } else if (data.agent_name.includes('Patent')) {
        setPatentStatus('COMPLETED');
        setPatentCount(data.items_found);
        setPatentTime(data.execution_time_ms);
      } else if (data.agent_name.includes('Market')) {
        setMarketStatus('COMPLETED');
        setMarketCount(data.items_found);
        setMarketTime(data.execution_time_ms);
      }
    });

    eventSource.addEventListener('agent_failed', (e: any) => {
      const data = JSON.parse(e.data);
      addLog(`⚠️ ${data.agent_name} warning: ${data.error}`, 'warning');
      if (data.agent_name.includes('Clinical')) setClinicalStatus('FAILED');
      if (data.agent_name.includes('Literature')) setLiteratureStatus('FAILED');
      if (data.agent_name.includes('Patent')) setPatentStatus('FAILED');
      if (data.agent_name.includes('Market')) setMarketStatus('FAILED');
    });

    eventSource.addEventListener('analysis_completed', (e: any) => {
      const data = JSON.parse(e.data);
      setQueryStatus('COMPLETED');
      setIndicationsCount(data.indications_count || 0);
      addLog(`Master Agent: Analysis complete. Synthesized ${data.indications_count} indications.`, 'success');
      eventSource.close();
    });

    // Fallback polling in case SSE is interrupted
    const interval = setInterval(async () => {
      if (!isMounted) return;
      try {
        const detail = await api.research.get(queryId);
        setDrugName(detail.normalized_drug_name || detail.drug_name);
        setQueryStatus(detail.status);
        if (detail.indications?.length > 0) {
          setIndicationsCount(detail.indications.length);
        }

        // Update agents
        detail.agent_runs.forEach((ar) => {
          if (ar.agent_name.includes('Clinical')) {
            setClinicalStatus(ar.status);
            setClinicalCount(ar.items_found);
            setClinicalTime(ar.execution_time_ms);
          } else if (ar.agent_name.includes('Literature')) {
            setLiteratureStatus(ar.status);
            setLiteratureCount(ar.items_found);
            setLiteratureTime(ar.execution_time_ms);
          } else if (ar.agent_name.includes('Patent')) {
            setPatentStatus(ar.status);
            setPatentCount(ar.items_found);
            setPatentTime(ar.execution_time_ms);
          } else if (ar.agent_name.includes('Market')) {
            setMarketStatus(ar.status);
            setMarketCount(ar.items_found);
            setMarketTime(ar.execution_time_ms);
          }
        });

        if (detail.status === 'COMPLETED' || detail.status === 'PARTIAL_FAILURE') {
          clearInterval(interval);
          eventSource.close();
        }
      } catch {
        // ignore
      }
    }, 2000);

    return () => {
      isMounted = false;
      clearInterval(interval);
      eventSource.close();
    };
  }, [queryId]);

  const addLog = (message: string, type: 'info' | 'success' | 'warning' | 'error') => {
    setLogs((prev) => [
      ...prev,
      { time: new Date().toLocaleTimeString(), message, type }
    ]);
  };

  const isCompleted = queryStatus === 'COMPLETED' || queryStatus === 'PARTIAL_FAILURE';

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-teal-500 animate-ping"></span>
            <span className="text-xs font-bold uppercase tracking-wider text-teal-600 font-mono">
              Live Agent Execution
            </span>
          </div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight mt-1">
            Investigating {drugName}
          </h1>
        </div>

        {isCompleted && (
          <button
            onClick={() => onNavigate('results', queryId)}
            className="px-6 py-2.5 bg-teal-600 hover:bg-teal-500 text-white rounded-lg font-bold text-sm shadow-md transition-all flex items-center gap-2 animate-in fade-in"
          >
            View Research Results ({indicationsCount} Indications)
            <ArrowRight className="w-4 h-4" />
          </button>
        )}
      </div>

      <DisclaimerBanner compact />

      {/* 4 Specialized Agent Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <AgentLiveCard
          name="Clinical Agent"
          type="clinical"
          status={clinicalStatus}
          itemsFound={clinicalCount}
          executionTimeMs={clinicalTime}
          sourceRepo="ClinicalTrials.gov"
          currentOperation={clinicalStatus === 'RUNNING' ? 'Fetching trials by condition...' : undefined}
        />

        <AgentLiveCard
          name="Literature Agent"
          type="literature"
          status={literatureStatus}
          itemsFound={literatureCount}
          executionTimeMs={literatureTime}
          sourceRepo="NCBI PubMed / PMC"
          currentOperation={literatureStatus === 'RUNNING' ? 'Classifying study hierarchies...' : undefined}
        />

        <AgentLiveCard
          name="Patent Agent"
          type="patent"
          status={patentStatus}
          itemsFound={patentCount}
          executionTimeMs={patentTime}
          sourceRepo="USPTO / PatentsView"
          currentOperation={patentStatus === 'RUNNING' ? 'Clustering assignee claims...' : undefined}
        />

        <AgentLiveCard
          name="Market Agent"
          type="market"
          status={marketStatus}
          itemsFound={marketCount}
          executionTimeMs={marketTime}
          sourceRepo="OpenFDA / Orange Book"
          currentOperation={marketStatus === 'RUNNING' ? 'Checking exclusivity & generics...' : undefined}
        />
      </div>

      {/* Live Event Log Stream */}
      <div className="bg-slate-900 text-slate-200 rounded-2xl p-6 shadow-xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-teal-400" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
              Master Agent Event Stream
            </h3>
          </div>
          <span className="text-[11px] font-mono text-slate-500">Real-Time Provenance Feed</span>
        </div>

        <div className="space-y-2 max-h-64 overflow-y-auto font-mono text-xs pr-2">
          {logs.map((log, index) => (
            <div key={index} className="flex items-start gap-3 text-slate-300">
              <span className="text-slate-500 text-[10px] select-none mt-0.5">{log.time}</span>
              <span className={
                log.type === 'success' ? 'text-teal-400' :
                log.type === 'warning' ? 'text-amber-400' :
                log.type === 'error' ? 'text-rose-400' : 'text-slate-300'
              }>
                {log.message}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
