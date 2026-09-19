import React from 'react';
import { Pill, Activity, PlusCircle, History, BookOpen, Shield, LogOut, User as UserIcon } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

interface NavbarProps {
  currentView: string;
  onNavigate: (view: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentView, onNavigate }) => {
  const { user, logout, isAdmin } = useAuth();

  return (
    <nav className="bg-slate-900 border-b border-slate-800 text-white sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div 
            className="flex items-center gap-3 cursor-pointer select-none"
            onClick={() => onNavigate(user ? 'dashboard' : 'landing')}
          >
            <div className="w-9 h-9 rounded-lg bg-teal-500/20 border border-teal-500/30 flex items-center justify-center text-teal-400">
              <Pill className="w-5 h-5" />
            </div>
            <div>
              <span className="text-lg font-bold tracking-tight text-white flex items-center gap-1.5">
                MEDISCAN <span className="text-teal-400">AI</span>
              </span>
              <span className="hidden sm:block text-[10px] text-slate-400 uppercase tracking-widest -mt-1 font-medium">
                Research Intelligence
              </span>
            </div>
          </div>

          {/* Navigation Links */}
          {user && (
            <div className="hidden md:flex items-center gap-1">
              <button
                onClick={() => onNavigate('dashboard')}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center gap-1.5 ${
                  currentView === 'dashboard'
                    ? 'bg-slate-800 text-teal-400 border border-slate-700'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                }`}
              >
                <Activity className="w-4 h-4" />
                Dashboard
              </button>

              <button
                onClick={() => onNavigate('new-analysis')}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center gap-1.5 ${
                  currentView === 'new-analysis'
                    ? 'bg-teal-600 text-white'
                    : 'bg-teal-500/10 text-teal-400 hover:bg-teal-500/20 border border-teal-500/30'
                }`}
              >
                <PlusCircle className="w-4 h-4" />
                New Analysis
              </button>

              <button
                onClick={() => onNavigate('history')}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center gap-1.5 ${
                  currentView === 'history'
                    ? 'bg-slate-800 text-teal-400 border border-slate-700'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                }`}
              >
                <History className="w-4 h-4" />
                History
              </button>

              <button
                onClick={() => onNavigate('methodology')}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center gap-1.5 ${
                  currentView === 'methodology'
                    ? 'bg-slate-800 text-teal-400 border border-slate-700'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                }`}
              >
                <BookOpen className="w-4 h-4" />
                Methodology
              </button>

              {isAdmin && (
                <button
                  onClick={() => onNavigate('admin')}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center gap-1.5 ${
                    currentView === 'admin'
                      ? 'bg-slate-800 text-teal-400 border border-slate-700'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                  }`}
                >
                  <Shield className="w-4 h-4" />
                  Admin
                </button>
              )}
            </div>
          )}

          {/* Right Action / Auth */}
          <div className="flex items-center gap-3">
            {user ? (
              <div className="flex items-center gap-3">
                <div className="hidden lg:flex flex-col text-right">
                  <span className="text-xs font-semibold text-slate-200">{user.full_name}</span>
                  <span className="text-[11px] text-teal-400 flex items-center justify-end gap-1">
                    {user.role} {user.organization && `• ${user.organization}`}
                  </span>
                </div>
                <button
                  onClick={logout}
                  className="p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-slate-800 transition-colors"
                  title="Log out"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <button
                  onClick={() => onNavigate('login')}
                  className="px-3.5 py-1.5 text-sm font-medium text-slate-300 hover:text-white transition-colors"
                >
                  Sign In
                </button>
                <button
                  onClick={() => onNavigate('signup')}
                  className="px-4 py-1.5 text-sm font-medium bg-teal-600 hover:bg-teal-500 text-white rounded-md shadow-sm transition-colors"
                >
                  Register
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};
