import React from 'react';
import { AlertCircle, CheckCircle2, Info, Loader2 } from 'lucide-react';

export function PageHeader({ title, subtitle, actions }) {
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', gap: 16, marginBottom: 22 }}>
      <div>
        <h1 style={{ fontSize: 22, fontWeight: 700, color: 'var(--text-main)' }}>{title}</h1>
        {subtitle && <p style={{ fontSize: 13.5, color: 'var(--text-secondary)', marginTop: 3 }}>{subtitle}</p>}
      </div>
      {actions && <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>{actions}</div>}
    </div>
  );
}

export function CodeEditor({ value, onChange, placeholder, minHeight = 220 }) {
  const lines = (value || '').split('\n').length;
  return (
    <div className="editor-box">
      <div className="editor-lines" aria-hidden="true">
        {Array.from({ length: Math.max(lines, 1) }, (_, i) => (
          <div key={i + 1}>{i + 1}</div>
        ))}
      </div>
      <textarea
        className="code-input"
        style={{ minHeight }}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        spellCheck={false}
      />
    </div>
  );
}

export function LoadingSpinner({ label = 'Analyzing...' }) {
  return (
    <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, color: 'var(--purple-dark)', fontSize: 13.5, fontWeight: 500 }}>
      <Loader2 size={16} className="spin" style={{ animation: 'spin 0.9s linear infinite' }} />
      <span>{label}</span>
      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

export function ErrorList({ errors = [] }) {
  if (!errors.length) return null;
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 14 }}>
      {errors.map((err, idx) => (
        <div
          key={idx}
          style={{
            background: 'var(--error-bg)',
            border: '1px solid #F5C2C9',
            borderRadius: 12,
            padding: '12px 16px',
            display: 'flex',
            gap: 12,
            alignItems: 'flex-start',
          }}
        >
          <AlertCircle size={18} color="var(--error)" style={{ flexShrink: 0, marginTop: 2 }} />
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
              <span className="badge badge-error">{err.error_type || 'Error'}</span>
              {err.line !== undefined && (
                <span style={{ fontSize: 12, color: 'var(--text-secondary)', fontWeight: 600 }}>
                  Line {err.line}, Col {err.column || 1}
                </span>
              )}
            </div>
            <div style={{ fontSize: 13.5, fontWeight: 600, color: 'var(--text-main)', marginTop: 4 }}>
              {err.message}
            </div>
            {err.suggestion && (
              <div style={{ fontSize: 12.5, color: 'var(--purple-dark)', marginTop: 4, display: 'flex', alignItems: 'center', gap: 6 }}>
                <Info size={14} /> <span>Suggestion: {err.suggestion}</span>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

export function StatusBanner({ ok, okText, errText }) {
  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 8,
        padding: '7px 14px',
        borderRadius: 10,
        fontSize: 13,
        fontWeight: 600,
        background: ok ? 'var(--success-bg)' : 'var(--error-bg)',
        color: ok ? 'var(--success)' : 'var(--error)',
      }}
    >
      {ok ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
      <span>{ok ? okText : errText}</span>
    </div>
  );
}
