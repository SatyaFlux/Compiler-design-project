import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronDown, ChevronRight, Pause, Play, RotateCcw, Square } from 'lucide-react';

function TreeNodeItem({ node, activeNodeId, expandedMap, onToggle }) {
  const hasChildren = node.children && node.children.length > 0;
  const isExpanded = expandedMap[node.id] !== false;
  const isActive = activeNodeId === node.id;

  const palette = {
    non_terminal: { bg: '#F0EAFE', border: '#8055D9', text: '#6240B5' },
    terminal: { bg: '#EAF8F3', border: '#15976B', text: '#15976B' },
    epsilon: { bg: '#F8F7FC', border: '#D6CCF0', text: '#77738A' },
  }[node.node_type || 'non_terminal'];

  return (
    <div style={{ marginLeft: 18, position: 'relative' }}>
      <motion.div
        initial={{ opacity: 0, x: -6 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.18 }}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 6,
          padding: '6px 12px',
          margin: '4px 0',
          borderRadius: 10,
          background: isActive ? '#8055D9' : palette.bg,
          color: isActive ? '#FFFFFF' : palette.text,
          border: `1.5px solid ${isActive ? '#6240B5' : palette.border}`,
          boxShadow: isActive ? '0 0 0 4px rgba(128,85,217,0.2)' : 'none',
          fontSize: 13,
          fontWeight: 600,
          cursor: hasChildren ? 'pointer' : 'default',
          transition: 'all 0.2s ease',
        }}
        onClick={() => hasChildren && onToggle(node.id)}
      >
        {hasChildren && (isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />)}
        <span className="mono">{node.label}</span>
        {node.node_type && (
          <span style={{ fontSize: 10, opacity: 0.75, textTransform: 'uppercase' }}>
            {node.node_type === 'non_terminal' ? 'NT' : node.node_type === 'terminal' ? 'T' : 'ε'}
          </span>
        )}
      </motion.div>

      {hasChildren && isExpanded && (
        <div style={{ borderLeft: '1.5px dashed #D6CCF0', marginLeft: 12, paddingLeft: 6 }}>
          {node.children.map((child) => (
            <TreeNodeItem
              key={child.id}
              node={child}
              activeNodeId={activeNodeId}
              expandedMap={expandedMap}
              onToggle={onToggle}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default function ParseTreeVisualizer({ tree, steps = [] }) {
  const [expandedMap, setExpandedMap] = useState({});
  const [stepIdx, setStepIdx] = useState(-1);
  const [playing, setPlaying] = useState(false);
  const [speedMs, setSpeedMs] = useState(600);

  useEffect(() => {
    setStepIdx(-1);
    setPlaying(false);
    setExpandedMap({});
  }, [tree]);

  useEffect(() => {
    if (!playing || !steps.length) return;
    const timer = setInterval(() => {
      setStepIdx((prev) => {
        if (prev + 1 >= steps.length) {
          setPlaying(false);
          return prev;
        }
        return prev + 1;
      });
    }, speedMs);
    return () => clearInterval(timer);
  }, [playing, steps, speedMs]);

  if (!tree) {
    return (
      <div className="card-lavender" style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: 36 }}>
        Run a grammar simulation or source code parse to view the interactive Parse Tree.
      </div>
    );
  }

  const activeStep = stepIdx >= 0 && stepIdx < steps.length ? steps[stepIdx] : null;
  const activeNodeId = activeStep?.active_node_id || activeStep?.node_id || null;

  const toggleNode = (id) => {
    setExpandedMap((prev) => ({ ...prev, [id]: prev[id] === false }));
  };

  return (
    <div>
      {steps.length > 0 && (
        <div
          className="card-lavender"
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: 12,
            padding: '12px 16px',
            marginBottom: 16,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <button
              className="btn btn-primary"
              onClick={() => {
                if (stepIdx >= steps.length - 1) setStepIdx(0);
                setPlaying((p) => !p);
              }}
            >
              {playing ? <Pause size={15} /> : <Play size={15} />}
              {playing ? 'Pause' : 'Play'}
            </button>
            <button className="btn btn-secondary" onClick={() => { setPlaying(false); setStepIdx(-1); }}>
              <Square size={14} /> Stop
            </button>
            <button className="btn btn-secondary" onClick={() => { setPlaying(false); setStepIdx(0); }}>
              <RotateCcw size={14} /> Reset
            </button>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: 13 }}>
            <span style={{ color: 'var(--text-secondary)', fontWeight: 600 }}>Speed:</span>
            <select
              value={speedMs}
              onChange={(e) => setSpeedMs(Number(e.target.value))}
              style={{
                padding: '6px 10px',
                borderRadius: 8,
                border: '1px solid var(--border-color)',
                background: '#FFFFFF',
                color: 'var(--text-main)',
              }}
            >
              <option value={1000}>0.5x (Slow)</option>
              <option value={600}>1x (Normal)</option>
              <option value={250}>2x (Fast)</option>
            </select>
            <span className="badge badge-purple">
              Step {Math.max(0, stepIdx + 1)} / {steps.length}
            </span>
          </div>

          {activeStep && (
            <div style={{ width: '100%', fontSize: 13, color: 'var(--purple-dark)', fontWeight: 600 }}>
              Active Action: <span className="mono">{activeStep.action}</span>
            </div>
          )}
        </div>
      )}

      <div className="card" style={{ overflowX: 'auto', maxHeight: 540, overflowY: 'auto' }}>
        <TreeNodeItem
          node={tree}
          activeNodeId={activeNodeId}
          expandedMap={expandedMap}
          onToggle={toggleNode}
        />
      </div>
    </div>
  );
}
