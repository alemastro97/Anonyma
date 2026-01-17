import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  FileText,
  FileStack,
  ListTodo,
  CreditCard,
  Settings as SettingsIcon,
  Shield,
  LogOut,
  Lock
} from 'lucide-react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const navItems = [
    { path: '/', label: 'Text Anonymization', icon: FileText, adminOnly: false },
    { path: '/document', label: 'Document Processing', icon: FileStack, adminOnly: false },
    { path: '/jobs', label: 'Jobs', icon: ListTodo, adminOnly: false },
    { path: '/pricing', label: 'Pricing', icon: CreditCard, adminOnly: false },
    { path: '/settings', label: 'Settings', icon: SettingsIcon, adminOnly: false },
    { path: '/admin', label: 'Admin Dashboard', icon: Shield, adminOnly: true },
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="h-screen bg-gradient-to-br from-orange-50 via-white to-purple-50 flex flex-col overflow-hidden">
      {/* Header with glassmorphism */}
      <header className="glass-card sticky top-0 z-50 border-b border-white/20 backdrop-blur-xl flex-shrink-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center">
                  <Lock className="w-5 h-5 text-white" />
                </div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
                  Anonyma
                </h1>
              </div>
              <p className="ml-2 text-sm text-muted-foreground hidden md:block">
                Enterprise PII Detection & Anonymization
              </p>
            </div>
            <div className="flex items-center gap-3">
              <Badge variant="outline" className="hidden sm:flex">
                v1.0.0
              </Badge>
              {user && (
                <>
                  <Badge
                    variant={
                      user.role === 'admin'
                        ? 'default'
                        : user.role === 'premium'
                        ? 'secondary'
                        : 'outline'
                    }
                    className="flex items-center gap-1"
                  >
                    {user.role === 'admin' && <Shield className="w-3 h-3" />}
                    {user.role === 'admin' && 'Admin'}
                    {user.role === 'premium' && 'Premium'}
                    {user.role === 'demo' && 'Demo'}
                  </Badge>
                  <span className="text-sm text-foreground font-medium hidden sm:inline">
                    {user.username}
                  </span>
                  <Button
                    onClick={handleLogout}
                    variant="ghost"
                    size="sm"
                    className="gap-2"
                  >
                    <LogOut className="w-4 h-4" />
                    <span className="hidden sm:inline">Logout</span>
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Navigation with glassmorphism */}
      <nav className="glass border-b border-white/10 sticky top-16 z-40 flex-shrink-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-1 overflow-x-auto">
            {navItems
              .filter((item) => !item.adminOnly || user?.role === 'admin')
              .map((item) => {
                const isActive = location.pathname === item.path;
                const Icon = item.icon;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`
                      inline-flex items-center gap-2 px-4 py-3 border-b-2 text-sm font-medium whitespace-nowrap
                      transition-all duration-200
                      ${
                        isActive
                          ? 'border-primary-500 text-primary-600 bg-primary-50/50'
                          : 'border-transparent text-muted-foreground hover:text-foreground hover:bg-white/30'
                      }
                    `}
                  >
                    <Icon className="w-4 h-4" />
                    {item.label}
                  </Link>
                );
              })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-grow overflow-y-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
          {children}
        </div>
      </main>

      {/* Footer with glassmorphism */}
      <footer className="glass-card border-t border-white/10 flex-shrink-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-muted-foreground">
            Powered by <span className="font-semibold text-primary-600">Presidio</span> + <span className="font-semibold text-secondary-600">Flair NER</span> +{' '}
            <span className="font-semibold text-accent-600">Custom Patterns</span>
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
