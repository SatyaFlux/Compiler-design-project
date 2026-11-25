import React, { useState } from 'react';
import {
  AlertTriangle,
  BookOpen,
  Braces,
  Code2,
  Cpu,
  FileCode,
  GitBranch,
  GraduationCap,
  Layers,
  LayoutDashboard,
  Menu,
  Network,
  Play,
  Save,
  ShieldCheck,
  Sparkles,
  Table2,
  X,
} from 'lucide-react';

export const NAV_SECTIONS = [
  {
    title: 'Overview',
    items: [
      { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    ],
  },
  {
    title: 'CFG & Parsing Theory',
    items: [
      { id: 'grammar', label: 'Grammar Editor', icon: BookOpen },
      { id: 'first_follow', label: 'FIRST & FOLLOW', icon: Layers },
      { id: 'll1_table', label: 'LL(1) Parsing Table', icon: Table2 },
    ],
  },
  {
    title: 'Compiler Pipeline',
    items: [
      { id: 'lexer', label: 'Lexical Analyzer', icon: Code2 },
      { id: 'syntax', label: 'Syntax Analyzer', icon: Braces },
      { id: 'parse_tree', label: 'Parse Tree', icon: GitBranch },
      { id: 'ast', label: 'Abstract Syntax Tree', icon: Network },
      { id: 'semantic', label: 'Semantic & Symbols', icon: ShieldCheck },
      { id: 'intermediate', label: 'Intermediate Code (TAC)', icon: FileCode },
      { id: 'optimizer', label: 'Code Optimization', icon: Sparkles },
      { id: 'execution', label: 'Code Execution', icon: Cpu },
    ],
  },
  {
    title: 'Practice & Diagnostics',
    items: [
      { id: 'errors', label: 'Error Simulator', icon: AlertTriangle },
      { id: 'quiz', label: 'Interactive Quiz', icon: GraduationCap },
    ],
  },
];

export default function MainLayout({
  activePage,
  onNavigate,
  onRunAll,
  onSaveExperiment,
  isRunning,
  children,
}) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="app-shell">
      <aside className={`sidebar ${mobileOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <div className="logo-badge">
            <GitBranch size={20} />
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 700, fontSize: 15, color: 'var(--text-main)' }}>CFG Experimenter</div>
            <div style={{ fontSize: 11.5, color: 'var(--text-secondary)' }}>Compiler Design Studio</div>
          </div>
          <button
            className="mobile-menu-btn btn btn-secondary"
            style={{ padding: 6 }}
            onClick={() => setMobileOpen(false)}
            aria-label="Close navigation"
          >
            <X size={16} />
          </button>
        </div>

        <nav className="sidebar-nav">
          {NAV_SECTIONS.map((sec) => (
            <div key={sec.title}>
              <div className="nav-section-label">{sec.title}</div>
              {sec.items.map((item) => {
                const Icon = item.icon;
                const active = activePage === item.id;
                return (
                  <button
                    key={item.id}
                    className={`nav-item ${active ? 'active' : ''}`}
                    onClick={() => {
                      onNavigate(item.id);
                      setMobileOpen(false);
                    }}
                  >
                    <Icon size={17} />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </div>
          ))}
        </nav>
      </aside>

      <div className="main-area">
        <header className="topbar">
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <button
              className="mobile-menu-btn btn btn-secondary"
              style={{ padding: 8 }}
              onClick={() => setMobileOpen(true)}
              aria-label="Open navigation"
            >
              <Menu size={18} />
            </button>
            <span className="badge badge-purple">White + Purple Academic Edition</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <button className="btn btn-secondary" onClick={onSaveExperiment}>
              <Save size={15} /> Save Experiment
            </button>
            <button className="btn btn-primary" onClick={onRunAll} disabled={isRunning}>
              <Play size={15} /> {isRunning ? 'Compiling...' : 'Compile & Run All'}
            </button>
          </div>
        </header>

        <main className="content-container">{children}</main>
      </div>
    </div>
  );
}
