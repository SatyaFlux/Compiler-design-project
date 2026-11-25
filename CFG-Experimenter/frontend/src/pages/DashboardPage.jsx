import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  ArrowRight,
  BookOpen,
  CheckCircle2,
  Code2,
  FlaskConical,
  GraduationCap,
  Layers,
  Play,
  Sparkles,
  Trash2,
} from 'lucide-react';
import { api } from '../services/api';
import { LoadingSpinner, PageHeader } from '../components/common/UI';

const LEARNING_MODULES = [
  { key: 'grammar', title: 'Grammar Editor', desc: 'Design & validate Context-Free Grammars', icon: BookOpen },
  { key: 'lexer', title: 'Lexical Analysis', desc: 'Tokenize source code with line/col tracking', icon: Code2 },
  { key: 'first_follow', title: 'FIRST & FOLLOW', desc: 'Compute Nullable, FIRST & FOLLOW sets', icon: Layers },
  { key: 'll1_table', title: 'LL(1) Parsing Table', desc: 'Build predictive tables & detect conflicts', icon: FlaskConical },
  { key: 'optimizer', title: 'Code Optimization', desc: 'Constant Folding, Propagation, DCE & CSE', icon: Sparkles },
  { key: 'quiz', title: 'Compiler Quiz', desc: 'Test your knowledge across 10 topics', icon: GraduationCap },
];

export default function DashboardPage({ onNavigate, onLoadExperiment }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadStats = async () => {
    setLoading(true);
    try {
      const res = await api.getDashboardStats();
      setData(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  const handleDelete = async (id) => {
    await api.deleteExperiment(id);
    loadStats();
  };

  if (loading && !data) {
    return <div className="card"><LoadingSpinner label="Loading Dashboard..." /></div>;
  }

  const stats = data?.stats || {
    experiments_count: 0,
    grammars_count: 0,
    quiz_attempts: 0,
    avg_quiz_score: 0,
    completed_modules: 0,
    total_modules: 13,
    progress_percent: 0,
  };

  return (
    <div>
      <PageHeader
        title="Welcome to CFG Experimenter"
        subtitle="Interactive Compiler Design Teaching Simulator — Real algorithms from Lexer to Execution."
        actions={
          <button className="btn btn-primary" onClick={() => onNavigate('lexer')}>
            <Play size={15} /> Start Experiment
          </button>
        }
      />

      {/* Welcome Banner & Learning Progress */}
      <div className="card-lavender" style={{ marginBottom: 22, display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', gap: 20 }}>
        <div style={{ maxWidth: 640 }}>
          <span className="badge badge-purple" style={{ marginBottom: 8 }}>Interactive Compiler Studio</span>
          <h2 style={{ fontSize: 20, fontWeight: 700, color: 'var(--text-main)' }}>
            Explore Every Compiler Phase Live
          </h2>
          <p style={{ fontSize: 13.5, color: 'var(--text-secondary)', marginTop: 6 }}>
            Write Context-Free Grammars or imperative programs, inspect real tokens, FIRST/FOLLOW sets, LL(1) tables,
            animated Parse Trees, ASTs, Symbol Tables, Three-Address Code, Optimizations, and Safe Execution.
          </p>
        </div>

        <div className="card" style={{ minWidth: 260, flex: '0 0 auto' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, fontWeight: 600, marginBottom: 8 }}>
            <span>Learning Progress</span>
            <span style={{ color: 'var(--purple-primary)' }}>{stats.progress_percent}%</span>
          </div>
          <div style={{ height: 10, borderRadius: 999, background: 'var(--purple-light)', overflow: 'hidden' }}>
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${stats.progress_percent}%` }}
              transition={{ duration: 0.6 }}
              style={{ height: '100%', background: 'linear-gradient(90deg, var(--purple-primary), var(--purple-dark))', borderRadius: 999 }}
            />
          </div>
          <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 8 }}>
            {stats.completed_modules} of {stats.total_modules} modules explored
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid-4" style={{ marginBottom: 24 }}>
        {[
          { label: 'Saved Experiments', value: stats.experiments_count, note: 'SQLite Persisted' },
          { label: 'Grammar Presets', value: stats.grammars_count, note: 'LL(1) & Conflict Demos' },
          { label: 'Quiz Attempts', value: stats.quiz_attempts, note: 'Interactive Assessments' },
          { label: 'Avg Quiz Score', value: `${stats.avg_quiz_score}%`, note: 'Across All Topics' },
        ].map((item) => (
          <div key={item.label} className="card card-hover">
            <div style={{ fontSize: 12.5, color: 'var(--text-secondary)', fontWeight: 600 }}>{item.label}</div>
            <div style={{ fontSize: 28, fontWeight: 700, color: 'var(--purple-dark)', margin: '6px 0 4px' }}>{item.value}</div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{item.note}</div>
          </div>
        ))}
      </div>

      {/* Learning Modules + Recent Experiments */}
      <div className="grid-2">
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
            <h3 style={{ fontSize: 16, fontWeight: 700 }}>Compiler Learning Modules</h3>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {LEARNING_MODULES.map((m) => {
              const Icon = m.icon;
              return (
                <button
                  key={m.key}
                  onClick={() => onNavigate(m.key)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 12,
                    padding: '12px 14px',
                    borderRadius: 12,
                    border: '1px solid var(--border-color)',
                    background: 'var(--bg-main)',
                    cursor: 'pointer',
                    textAlign: 'left',
                    transition: 'all 0.18s ease',
                  }}
                >
                  <div style={{ width: 36, height: 36, borderRadius: 10, background: 'var(--purple-light)', color: 'var(--purple-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                    <Icon size={18} />
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: 14, color: 'var(--text-main)' }}>{m.title}</div>
                    <div style={{ fontSize: 12.5, color: 'var(--text-secondary)' }}>{m.desc}</div>
                  </div>
                  <ArrowRight size={16} color="var(--purple-primary)" />
                </button>
              );
            })}
          </div>
        </div>

        <div className="card">
          <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 14 }}>Recent Experiments</h3>
          {!(data?.recent_experiments?.length) ? (
            <div className="card-lavender" style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: 28 }}>
              No experiments saved yet. Click "Save Experiment" in the top bar to save your work.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {data.recent_experiments.map((exp) => (
                <div
                  key={exp.id}
                  style={{
                    border: '1px solid var(--border-color)',
                    borderRadius: 12,
                    padding: '12px 14px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    gap: 12,
                  }}
                >
                  <div style={{ minWidth: 0 }}>
                    <div style={{ fontWeight: 600, fontSize: 14, color: 'var(--text-main)' }}>{exp.title}</div>
                    <div className="mono" style={{ fontSize: 12, color: 'var(--text-secondary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: 280 }}>
                      {exp.source_code.split('\n')[0]}
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: 8, flexShrink: 0 }}>
                    <button className="btn btn-soft" style={{ padding: '6px 12px', fontSize: 12.5 }} onClick={() => onLoadExperiment(exp)}>
                      <CheckCircle2 size={14} /> Load
                    </button>
                    <button className="btn btn-secondary" style={{ padding: '6px 10px' }} onClick={() => handleDelete(exp.id)} title="Delete experiment">
                      <Trash2 size={14} color="var(--error)" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
