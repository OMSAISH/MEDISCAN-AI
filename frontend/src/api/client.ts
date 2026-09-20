import {
  User,
  Token,
  DrugValidation,
  ResearchSummary,
  ResearchDetail,
  IndicationEvidenceList,
  Report,
  ReportFormat,
  AdminOverview,
  AuditLogItem
} from '../types';

const API_BASE = (import.meta as any).env?.VITE_API_BASE ||
  (typeof window !== 'undefined' && (window.location.port === '5173' || window.location.port === '3000')
    ? `${window.location.protocol}//${window.location.hostname}:8000/api/v1`
    : '/api/v1');

class ApiClient {
  private getToken(): string | null {
    if (typeof window !== 'undefined') {
      const urlParams = new URLSearchParams(window.location.search);
      const queryToken = urlParams.get('token');
      if (queryToken) {
        localStorage.setItem('mediscan_token', queryToken);
        return queryToken;
      }
    }
    return localStorage.getItem('mediscan_token');
  }

  private setToken(token: string | null) {
    if (token) {
      localStorage.setItem('mediscan_token', token);
    } else {
      localStorage.removeItem('mediscan_token');
    }
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> || {})
    };

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers
    });

    if (response.status === 401) {
      this.setToken(null);
      // Optional trigger for auth redirect
    }

    if (!response.ok) {
      let errorMessage = 'An error occurred during API request.';
      try {
        const errorData = await response.json();
        if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        } else if (Array.isArray(errorData.detail)) {
          errorMessage = errorData.detail.map((d: any) => d.msg || JSON.stringify(d)).join(', ');
        } else if (errorData.message) {
          errorMessage = errorData.message;
        }
      } catch {
        if (response.statusText) {
          errorMessage = `${response.status}: ${response.statusText}`;
        }
      }
      throw new Error(errorMessage);
    }

    return response.json();
  }

  // Auth endpoints
  auth = {
    register: async (data: { email: string; password: string; full_name: string; organization?: string }): Promise<User> => {
      return this.request<User>('/auth/register', {
        method: 'POST',
        body: JSON.stringify(data)
      });
    },
    login: async (email: string, password: string): Promise<Token> => {
      const data = await this.request<Token>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password })
      });
      this.setToken(data.access_token);
      return data;
    },
    me: async (): Promise<User> => {
      return this.request<User>('/auth/me');
    },
    logout: async (): Promise<void> => {
      try {
        await this.request('/auth/logout', { method: 'POST' });
      } finally {
        this.setToken(null);
      }
    }
  };

  // Drug validation & normalization
  drugs = {
    validate: async (name: string): Promise<DrugValidation> => {
      return this.request<DrugValidation>(`/drugs/validate?name=${encodeURIComponent(name)}`);
    },
    search: async (q: string): Promise<any[]> => {
      return this.request<any[]>(`/drugs/search?q=${encodeURIComponent(q)}`);
    }
  };

  // Research analysis endpoints
  research = {
    create: async (data: {
      drug_name: string;
      research_question?: string;
      enable_clinical?: boolean;
      enable_literature?: boolean;
      enable_patent?: boolean;
      enable_market?: boolean;
    }): Promise<ResearchDetail> => {
      return this.request<ResearchDetail>('/research', {
        method: 'POST',
        body: JSON.stringify(data)
      });
    },
    get: async (id: string): Promise<ResearchDetail> => {
      return this.request<ResearchDetail>(`/research/${id}`);
    },
    history: async (limit = 20, offset = 0): Promise<ResearchSummary[]> => {
      return this.request<ResearchSummary[]>(`/research/history?limit=${limit}&offset=${offset}`);
    },
    delete: async (id: string): Promise<void> => {
      await this.request(`/research/${id}`, { method: 'DELETE' });
    },
    getEventSource: (id: string): EventSource => {
      const token = this.getToken();
      // Use query or header if supported by EventSource
      return new EventSource(`${API_BASE}/research/${id}/stream`);
    }
  };

  // Evidence endpoints
  evidence = {
    get: async (indicationId: string): Promise<IndicationEvidenceList> => {
      return this.request<IndicationEvidenceList>(`/evidence/${indicationId}`);
    }
  };

  // Report generation endpoints
  reports = {
    generate: async (queryId: string, format: ReportFormat): Promise<Report> => {
      return this.request<Report>(`/reports/${queryId}/generate`, {
        method: 'POST',
        body: JSON.stringify({ report_format: format })
      });
    },
    downloadUrl: (reportId: string): string => {
      return `${API_BASE}/reports/${reportId}/download`;
    }
  };

  // Admin endpoints
  admin = {
    overview: async (): Promise<AdminOverview> => {
      return this.request<AdminOverview>('/admin/overview');
    },
    auditLogs: async (limit = 50, offset = 0): Promise<AuditLogItem[]> => {
      return this.request<AuditLogItem[]>(`/admin/audit-logs?limit=${limit}&offset=${offset}`);
    }
  };
}

export const api = new ApiClient();
