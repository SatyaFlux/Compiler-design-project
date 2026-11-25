import React, { useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle2, Play, Plus, Trash2 } from 'lucide-react';
import { api } from '../services/api';
import { CodeEditor, ErrorList, LoadingSpinner, PageHeader, StatusBanner } from '../components/common/UI';
import ParseTreeVisualizer from '../components/visualizers/ParseTreeVisualizer';

export function GrammarEditorPage({ grammarText, setGrammarText, sampleInput, setSampleInput }) {
  const [presets, setPresets] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [newLhs, setNewLhs] = useState('');
  const [newRhs, setNewRhs] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.getGrammarPresets().then((d) => setPresets(d.presets || [])).catch(() => {});
  }, []);

  const handleValidate = async (text = grammarText) => {
    setLoading(true);
    try {
      const res = await api.validateGrammar(text);
      setAnalysis(res);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleValidate(grammarText);
  }, []);

  const addProduction = () => {
    if (!newLhs.trim() || !newRhs.trim()) return;
    const line = `${newLhs.trim()} -> ${newRhs.trim()}`;
    const updated = grammarText.trim() ? `${grammarText.trim()}\n${line}` : line;
    setGrammarText(updated);
    setNewLhs('');
    setNewRhs('');
    handleValidate(updated);
  };

  const deleteProductionLine = (idx) => {
    const lines = grammarText.split('\n').filter((_, i) => i !== idx);
    const updated = lines.join('\n');
    setGrammarText(updated);
    handleValidate(updated);
  };

  return (
    <div>
      <PageHeader
        title="Context-Free Grammar Editor"
        subtitle="Define CFG productions (use 'ε' for epsilon), load presets, and validate grammar properties."
        actions={
          <button className="btn btn-primary" onClick={() => handleValidate()} disabled={loading}>
            <Play size={15} /> Validate Grammar
          </button>
        }
      />

      <div className="grid-2">
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12, gap: 8, flexWrap: 'wrap' }}>
            <h3 style={{ fontSize: 15.5, fontWeight: 700 }}>CFG Productions</h3>
            <select
              onChange={(e) => {
                const p = presets.find((x) => String(x.id) === e.target.value);
                if (p) {
                  setGrammarText(p.productions_text);
                  if (p.sample_input) setSampleInput(p.sample_input);
                  handleValidate(p.productions_text);
                }
              }}
              defaultValue=""
              style={{ padding: '6px 10px', borderRadius: 8, border: '1px solid var(--border-color)', fontSize: 13 }}
            >
              <option value="" disabled>Load Preset Grammar...</option>
              {presets.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>

          <CodeEditor
            value={grammarText}
            onChange={setGrammarText}
            placeholder={"E -> T E'\nE' -> + T E' | - T E' | ε\nT -> num | id"}
            minHeight={200}
          />

          {/* Quick Add Production */}
          <div style={{ display: 'flex', gap: 8, marginTop: 12, flexWrap: 'wrap' }}>
            <input
              value={newLhs}
              onChange={(e) => setNewLhs(e.target.value)}
              placeholder="LHS (e.g. F)"
              className="mono"
              style={{ width: 100, padding: '8px 10px', borderRadius: 8, border: '1px solid var(--border-color)', fontSize: 13 }}
            />
            <span style={{ alignSelf: 'center', fontWeight: 700, color: 'var(--purple-primary)' }}>-&gt;</span>
            <input
              value={newRhs}
              onChange={(e) => setNewRhs(e.target.value)}
              placeholder="RHS (e.g. ( E ) | num)"
              className="mono"
              style={{ flex: 1, minWidth: 160, padding: '8px 10px', borderRadius: 8, border: '1px solid var(--border-color)', fontSize: 13 }}
            />
            <button className="btn btn-soft" onClick={addProduction}>
              <Plus size={15} /> Add
            </button>
          </div>

          {/* Line-by-line delete */}
          <div style={{ marginTop: 14, display: 'flex', flexDirection: 'column', gap: 6 }}>
            {grammarText.split('\n').map((line, idx) =>
              line.trim() ? (
                <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '6px 10px', borderRadius: 8, background: 'var(--lavender-soft)', fontSize: 12.5 }}>
                  <span className="mono">{line}</span>
                  <button onClick={() => deleteProductionLine(idx)} style={{ background: 'none', border: 'none', cursor: 'pointer' }} title="Delete rule">
                    <Trash2 size={14} color="var(--error)" />
                  </button>
                </div>
              ) : null
            )}
          </div>
        </div>

        <div className="card">
          <h3 style={{ fontSize: 15.5, fontWeight: 700, marginBottom: 14 }}>Grammar Analysis</h3>
          {loading ? (
            <LoadingSpinner />
          ) : analysis ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <StatusBanner ok={analysis.valid} okText="Valid Context-Free Grammar" errText="Invalid Grammar Syntax" />
              <ErrorList errors={analysis.errors} />

              <div className="grid-2" style={{ gap: 12 }}>
                <div className="card-lavender" style={{ padding: 14 }}>
                  <div style={{ fontSize: 12, color: 'var(--text-secondary)', fontWeight: 600 }}>Start Symbol</div>
                  <div className="mono" style={{ fontSize: 18, fontWeight: 700, color: 'var(--purple-dark)', marginTop: 4 }}>
                    {analysis.start_symbol || '—'}
                  </div>
                </div>
                <div className="card-lavender" style={{ padding: 14 }}>
                  <div style={{ fontSize: 12, color: 'var(--text-secondary)', fontWeight: 600 }}>Non-Terminals ({analysis.non_terminals?.length || 0})</div>
                  <div className="mono" style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-main)', marginTop: 6 }}>
                    {(analysis.non_terminals || []).join(', ') || '—'}
                  </div>
                </div>
              </div>

              <div className="card-lavender" style={{ padding: 14 }}>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)', fontWeight: 600 }}>Terminals ({analysis.terminals?.length || 0})</div>
                <div className="mono" style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-main)', marginTop: 6 }}>
                  {(analysis.terminals || []).join(', ') || '—'}
                </div>
              </div>

              {analysis.warnings?.length > 0 && (
                <div style={{ background: 'var(--warning-bg)', border: '1px solid #F2D7A5', borderRadius: 12, padding: 12 }}>
                  <div style={{ fontWeight: 700, fontSize: 13, color: 'var(--warning)', display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
                    <AlertTriangle size={15} /> Warnings
                  </div>
                  {analysis.warnings.map((w, i) => (
                    <div key={i} style={{ fontSize: 13, color: 'var(--text-main)' }}>• {w}</div>
                  ))}
                </div>
              )}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}

export function FirstFollowPage({ grammarText }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const compute = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getFirstFollow(grammarText);
      setData(res);
    } catch (e) {
      setError(e.data?.errors || [{ error_type: 'GrammarError', message: e.message }]);
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    compute();
  }, [grammarText]);

  return (
    <div>
      <PageHeader
        title="FIRST and FOLLOW Sets"
        subtitle="Fixed-point computation of Nullable non-terminals, FIRST(X), and FOLLOW(A) with step trace."
        actions={<button className="btn btn-primary" onClick={compute} disabled={loading}><Play size={15} /> Recompute</button>}
      />

      {loading && <LoadingSpinner label="Computing FIRST & FOLLOW..." />}
      <ErrorList errors={error || []} />

      {data && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14, flexWrap: 'wrap' }}>
              <h3 style={{ fontSize: 15.5, fontWeight: 700 }}>FIRST & FOLLOW Table</h3>
              <span className="badge badge-purple">
                Nullable: {data.nullable?.length ? data.nullable.join(', ') : 'None'}
              </span>
            </div>
            <div className="data-table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Non-Terminal</th>
                    <th>Nullable</th>
                    <th>FIRST Set</th>
                    <th>FOLLOW Set</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.keys(data.first || {}).map((nt) => (
                    <tr key={nt}>
                      <td className="mono" style={{ fontWeight: 700, color: 'var(--purple-dark)' }}>{nt}</td>
                      <td>
                        {data.nullable.includes(nt) ? (
                          <span className="badge badge-success">Yes (ε)</span>
                        ) : (
                          <span style={{ color: 'var(--text-secondary)' }}>No</span>
                        )}
                      </td>
                      <td className="mono">{`{ ${data.first[nt].join(', ')} }`}</td>
                      <td className="mono">{`{ ${data.follow[nt].join(', ')} }`}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="card">
            <h3 style={{ fontSize: 15.5, fontWeight: 700, marginBottom: 12 }}>Step-by-Step Calculation Trace</h3>
            <div className="data-table-wrap" style={{ maxHeight: 320, overflowY: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Phase</th>
                    <th>Iter</th>
                    <th>Symbol</th>
                    <th>Production</th>
                    <th>Update</th>
                  </tr>
                </thead>
                <tbody>
                  {(data.steps || []).map((s, idx) => (
                    <tr key={idx}>
                      <td><span className="badge badge-purple">{s.phase}</span></td>
                      <td>{s.iteration}</td>
                      <td className="mono" style={{ fontWeight: 600 }}>{s.symbol}</td>
                      <td className="mono">{s.rule}</td>
                      <td>{s.detail}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export function LL1ParsingPage({ grammarText, sampleInput, setSampleInput }) {
  const [tableData, setTableData] = useState(null);
  const [simResult, setSimResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const buildAndSimulate = async () => {
    setLoading(true);
    setError(null);
    try {
      const tbl = await api.getLL1Table(grammarText);
      setTableData(tbl);
      if (tbl.is_ll1 && sampleInput.trim()) {
        const sim = await api.simulateLL1(grammarText, sampleInput);
        setSimResult(sim);
      } else {
        setSimResult(null);
      }
    } catch (e) {
      setError(e.data?.errors || [{ error_type: 'GrammarError', message: e.message }]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    buildAndSimulate();
  }, [grammarText]);

  return (
    <div>
      <PageHeader
        title="LL(1) Parsing Table & Stack Simulator"
        subtitle="Constructs predictive parsing table M[A, a], detects LL(1) conflicts, and simulates Stack | Input | Action."
        actions={<button className="btn btn-primary" onClick={buildAndSimulate} disabled={loading}><Play size={15} /> Simulate LL(1)</button>}
      />

      {loading && <LoadingSpinner label="Building LL(1) Table..." />}
      <ErrorList errors={error || []} />

      {tableData && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14, flexWrap: 'wrap', gap: 10 }}>
              <h3 style={{ fontSize: 15.5, fontWeight: 700 }}>LL(1) Parsing Table</h3>
              <StatusBanner
                ok={tableData.is_ll1}
                okText="Grammar is LL(1) — Zero Conflicts"
                errText={`Not LL(1) — ${tableData.conflicts?.length || 0} Conflict(s) Detected`}
              />
            </div>

            {tableData.conflicts?.length > 0 && (
              <div style={{ background: 'var(--error-bg)', border: '1px solid #F5C2C9', borderRadius: 10, padding: 12, marginBottom: 14 }}>
                {tableData.conflicts.map((c, idx) => (
                  <div key={idx} style={{ fontSize: 13, color: 'var(--error)', fontWeight: 600 }}>
                    {c.type} Conflict at M[{c.non_terminal}, {c.terminal}]: {c.productions.join('  vs  ')}
                  </div>
                ))}
              </div>
            )}

            <div className="data-table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Non-Terminal</th>
                    {(tableData.terminals || []).map((t) => (
                      <th key={t} className="mono">{t}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {(tableData.non_terminals || []).map((nt) => (
                    <tr key={nt}>
                      <td className="mono" style={{ fontWeight: 700, color: 'var(--purple-dark)' }}>{nt}</td>
                      {(tableData.terminals || []).map((t) => {
                        const cell = tableData.table?.[nt]?.[t] || [];
                        const isConflict = cell.length > 1;
                        return (
                          <td
                            key={t}
                            className="mono"
                            style={{
                              fontSize: 12.5,
                              background: isConflict ? 'var(--error-bg)' : cell.length ? '#FAF8FE' : 'transparent',
                              color: isConflict ? 'var(--error)' : 'var(--text-main)',
                              fontWeight: cell.length ? 600 : 400,
                            }}
                          >
                            {cell.length ? cell.join(' | ') : '—'}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="card">
            <h3 style={{ fontSize: 15.5, fontWeight: 700, marginBottom: 12 }}>Stack-Based Input Simulation</h3>
            <div style={{ display: 'flex', gap: 10, marginBottom: 16, flexWrap: 'wrap' }}>
              <input
                value={sampleInput}
                onChange={(e) => setSampleInput(e.target.value)}
                placeholder="Space-separated tokens, e.g.: id + num * id"
                className="mono"
                style={{ flex: 1, minWidth: 240, padding: '10px 14px', borderRadius: 10, border: '1px solid var(--border-color)', fontSize: 13.5 }}
              />
              <button className="btn btn-primary" onClick={buildAndSimulate} disabled={!tableData.is_ll1}>
                <Play size={15} /> Parse Input String
              </button>
            </div>

            {simResult && (
              <>
                <div style={{ marginBottom: 14 }}>
                  <StatusBanner
                    ok={simResult.accepted}
                    okText="Input String ACCEPTED by LL(1) Parser"
                    errText={simResult.error || 'Input String REJECTED'}
                  />
                </div>
                <div className="data-table-wrap" style={{ maxHeight: 320, overflowY: 'auto', marginBottom: 20 }}>
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Step</th>
                        <th>Stack</th>
                        <th>Input</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(simResult.steps || []).map((s) => (
                        <tr key={s.step}>
                          <td>{s.step}</td>
                          <td className="mono">{s.stack}</td>
                          <td className="mono">{s.input}</td>
                          <td className="mono" style={{ fontWeight: 600, color: s.action.startsWith('ERROR') ? 'var(--error)' : s.action === 'ACCEPT' ? 'var(--success)' : 'var(--purple-dark)' }}>
                            {s.action}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <h4 style={{ fontSize: 14.5, fontWeight: 700, marginBottom: 10 }}>Animated LL(1) Parse Tree</h4>
                <ParseTreeVisualizer tree={simResult.parse_tree} steps={simResult.steps} />
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
