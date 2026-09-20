import React, { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { Navbar } from './components/layout/Navbar';
import { Footer } from './components/layout/Footer';

// Pages
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { SignupPage } from './pages/SignupPage';
import { DashboardPage } from './pages/DashboardPage';
import { NewAnalysisPage } from './pages/NewAnalysisPage';
import { LiveAnalysisPage } from './pages/LiveAnalysisPage';
import { ResultsPage } from './pages/ResultsPage';
import { HistoryPage } from './pages/HistoryPage';
import { MethodologyPage } from './pages/MethodologyPage';
import { AdminPage } from './pages/AdminPage';

const AppContent: React.FC = () => {
  const { user, loading } = useAuth();

  const getInitialState = () => {
    const params = new URLSearchParams(window.location.search);
    const viewParam = params.get('view') || window.location.hash.replace('#', '');
    const idParam = params.get('id') || '05272b5e-9e1e-468f-91a4-63801f8f4565';
    const drugParam = params.get('drug') || 'Metformin';
    return {
      view: viewParam || 'landing',
      id: idParam,
      drug: drugParam,
    };
  };

  const initialState = getInitialState();
  const [currentView, setCurrentView] = useState<string>(initialState.view);
  const [activeQueryId, setActiveQueryId] = useState<string>(initialState.id);
  const [initialDrug, setInitialDrug] = useState<string>(initialState.drug);

  const navigate = (view: string, id?: string) => {
    if (view.startsWith('new-analysis:')) {
      const drug = decodeURIComponent(view.split(':')[1]);
      setInitialDrug(drug);
      setCurrentView('new-analysis');
      window.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }

    if (id) {
      setActiveQueryId(id);
    }
    setCurrentView(view);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // If initial load finishes and user is logged in on landing (and no explicit view param), show dashboard
  React.useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (!params.get('view') && !loading && user && currentView === 'landing') {
      setCurrentView('dashboard');
    }
  }, [loading, user]);

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
      <Navbar currentView={currentView} onNavigate={navigate} />

      <main className="flex-1">
        {currentView === 'landing' && <LandingPage onNavigate={navigate} />}
        {currentView === 'login' && <LoginPage onNavigate={navigate} />}
        {currentView === 'signup' && <SignupPage onNavigate={navigate} />}
        {currentView === 'dashboard' && <DashboardPage onNavigate={navigate} />}
        {currentView === 'new-analysis' && (
          <NewAnalysisPage initialDrug={initialDrug} onNavigate={navigate} />
        )}
        {currentView === 'live-analysis' && (
          <LiveAnalysisPage queryId={activeQueryId} onNavigate={navigate} />
        )}
        {currentView === 'results' && (
          <ResultsPage queryId={activeQueryId} onNavigate={navigate} />
        )}
        {currentView === 'history' && <HistoryPage onNavigate={navigate} />}
        {currentView === 'methodology' && <MethodologyPage />}
        {currentView === 'admin' && <AdminPage />}
      </main>

      <Footer onNavigate={navigate} />
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App;
