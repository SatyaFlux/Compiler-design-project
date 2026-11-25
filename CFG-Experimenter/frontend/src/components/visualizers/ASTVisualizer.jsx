import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronDown, ChevronRight, Code2, Network } from 'lucide-react';

function ASTNodeBranch({ label, data, depth = 0 }) {
  const [open, setOpen] = useState(true);

  if (data === null || data === undefined) return null;

  if (Array.isArray(data)) {
    if (!data.length) return null;
    return (
      <div style={{ marginLeft: depth > 0 ? 16 : 0 }}>
        {data.map((item, idx) => (
          <ASTNodeBranch key={idx} label={`${label}[${idx}]`} data={item} depth={depth + 1} />
        ))}
      </div>
    );
  }

  if (typeof data !== 'object') {
    return (
      <div style={{ marginLeft: 18, fontSize: 13, padding: '3px 0', color: 'var(--text-secondary)' }}>
        <span style={{ fontWeight: 600 }}>{label}:</span>{' '}
        <span className="mono" style={{ color: 'var(--purple-dark)', fontWeight: 600 }}>{String(data)}</span>
      </div>
    );
  }

  const nodeTitle = data.type || label;
  const badgeExtra = data.op || data.name || (data.value !== undefined ? String(data.value) : null);
  const childKeys = Object.keys(data).filter((k) => !['type', 'line', 'column'].includes(k));

  return (
    <div style={{ marginLeft: depth > 0 ? 18 : 0, marginTop: 6 }}>
      <motion.div
        initial={{ opacity: 0, y: 4 }}
        animate={{ opacity: 1, y: 0 }}
        onClick={() => setOpen((o) => !o)}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 8,
          padding: '6px 12px',
          borderRadius: 10,
          background: 'var(--purple-light)',
          border: '1px solid #D6CCF0',
          cursor: 'pointer',
          fontSize: 13,
          fontWeight: 600,
          color: 'var(--purple-dark)',
        }}
      >
        {open ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        <span>{nodeTitle}</span>
        {badgeExtra !== null && (
          <span className="badge" style={{ background: '#FFFFFF', color: 'var(--purple-primary)' }}>
            {badgeExtra}
          </span>
        )}
      </motion.div>
      {open && (
        <div style={{ borderLeft: '1.5px solid var(--border-color)', marginLeft: 12, paddingLeft: 8, marginTop: 4 }}>
          {childKeys.map((k) => (
            <ASTNodeBranch key={k} label={k} data={data[k]} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function ASTVisualizer({ ast }) {
  const [viewMode, setViewMode] = useState('tree');

  if (!ast) {
    return (
      <div className="card-lavender" style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: 36 }}>
        Parse valid source code to inspect the Abstract Syntax Tree.
      </div>
    );
  }

  return (
    <div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 14 }}>
        <button
          className={`btn ${viewMode === 'tree' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setViewMode('tree')}
        >
          <Network size={15} /> Visual Tree
        </button>
        <button
          className={`btn ${viewMode === 'json' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setViewMode('json')}
        >
          <Code2 size={15} /> JSON Representation
        </button>
      </div>

      {viewMode === 'tree' ? (
        <div className="card" style={{ maxHeight: 540, overflowY: 'auto' }}>
          <ASTNodeBranch label="Program" data={ast} />
        </div>
      ) : (
        <pre
          className="card mono"
          style={{
            background: '#FCFBFF',
            fontSize: 12.5,
            maxHeight: 540,
            overflow: 'auto',
            color: 'var(--text-main)',
          }}
        >
          {JSON.stringify(ast, null, 2)}
        </pre>
      )}
    </div>
  );
}
