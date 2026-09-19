import React from 'react';
import { EvidenceStrength, QueryStatus, AgentStatus } from '../../types';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'strong' | 'moderate' | 'limited' | 'insufficient' | 'success' | 'running' | 'warning' | 'danger';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ children, variant = 'default', className = '' }) => {
  const variantStyles = {
    default: 'bg-slate-100 text-slate-700 border-slate-200',
    strong: 'bg-emerald-50 text-emerald-700 border-emerald-200 font-semibold',
    moderate: 'bg-blue-50 text-blue-700 border-blue-200 font-semibold',
    limited: 'bg-amber-50 text-amber-700 border-amber-200',
    insufficient: 'bg-slate-100 text-slate-500 border-slate-200',
    success: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    running: 'bg-teal-50 text-teal-700 border-teal-200 animate-pulse',
    warning: 'bg-amber-50 text-amber-700 border-amber-200',
    danger: 'bg-rose-50 text-rose-700 border-rose-200'
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${variantStyles[variant]} ${className}`}>
      {children}
    </span>
  );
};

export const EvidenceStrengthBadge: React.FC<{ strength: EvidenceStrength }> = ({ strength }) => {
  const variantMap: Record<EvidenceStrength, 'strong' | 'moderate' | 'limited' | 'insufficient'> = {
    Strong: 'strong',
    Moderate: 'moderate',
    Limited: 'limited',
    Insufficient: 'insufficient'
  };

  return (
    <Badge variant={variantMap[strength] || 'default'}>
      {strength} Evidence
    </Badge>
  );
};

export const StatusBadge: React.FC<{ status: QueryStatus | AgentStatus }> = ({ status }) => {
  if (status === 'COMPLETED') return <Badge variant="success">Completed</Badge>;
  if (status === 'RUNNING') return <Badge variant="running">Running...</Badge>;
  if (status === 'QUEUED') return <Badge variant="default">Queued</Badge>;
  if (status === 'PARTIAL_FAILURE') return <Badge variant="warning">Partial Failure</Badge>;
  if (status === 'FAILED') return <Badge variant="danger">Failed</Badge>;
  return <Badge variant="default">{status}</Badge>;
};
