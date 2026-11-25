import React from 'react';
import { motion } from 'framer-motion';
import { Play, Sparkles, Terminal } from 'lucide-react';
import { CodeEditor, ErrorList, PageHeader, StatusBanner } from '../components/common/UI';
import ParseTreeVisualizer from '../components/visualizers/ParseTreeVisualizer';
import ASTVisualizer from '../components/visualizers/ASTVisualizer';

function SourceEditorCard({ sourceCode, setSourceCode, onCompile, isRunning }) {
  return (
    <div className="card" style={{ marginBottom: 20 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
        <h3 style={{ fontSize: 15, fontWeight: 700 }}>Source Code Input</h3>
        <button className="btn btn-primary" onClick={onCompile} disabled={isRunning}>
          <Play size={14} /> {isRunning ? 'Running...' : 'Run Pipeline'}
        </button>
      </div>
      <CodeEditor value={sourceCode} onChange={setSourceCode} minHeight={160} />
    </div>
  );
}

export function LexerPage({ sourceCode, setSourceCode, pipeline, onCompile, isRunning }) {
  const tokens = (pipeline?.tokens || []).filter((t) => t.token_type !== 'EOF');
  const errors = pipeline?.lexical_errors || [];

  return (
    <div>
      <PageHeader title="Lexical Analyzer" subtitle="Character-by-character scanner with line/column tracking and token classification." />
      <SourceEditorCard sourceCode={sourceCode} setSourceCode={setSourceCode} onCompile={onCompile} isRunning={isRunning} />

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14, flexWrap: 'wrap', gap: 10 }}>
          <h3 style={{ fontSize: 15.5, fontWeight: 700 }}>Generated Token Stream ({tokens.length})</h3>
          <StatusBanner ok={errors.length === 0} okText="Zero Lexical Errors" errText={`${errors.length} Lexical Error(s)`} />
        </div>
        <ErrorList errors={errors} />
        <div className="data-table-wrap" style={{ marginTop: 12, maxHeight: 400, overflowY: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Token Type</th>
                <th>Lexeme</th>
                <th>Line</th>
                <th>Column</th>
              </tr>
            </thead>
            <tbody>
              {tokens.map((tok, i) => (
                <motion.tr
                  key={`${tok.line}-${tok.column}-${i}`}
                  initial={{ opacity: 0, x: -4 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.15, delay: Math.min(i * 0.015, 0.3) }}
                >
                  <td>{i + 1}</td>
                  <td><span className="badge badge-purple">{tok.token_type}</span></td>
                  <td className="mono" style={{ fontWeight: 600 }}>{tok.lexeme}</td>
                  <td>{tok.line}</td>
                  <td>{tok.column}</td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export function SyntaxPage({ sourceCode, setSourceCode, pipeline, onCompile, isRunning }) {
  const errors = [...(pipeline?.lexical_errors || []), ...(pipeline?.syntax_errors || [])];
  const steps = pipeline?.parse_steps || [];

  return (
    <div>
      <PageHeader title="Syntax Analyzer" subtitle="Recursive Descent Parser with grammar rule tracing and panic-mode error recovery." />
      <SourceEditorCard sourceCode={sourceCode} setSourceCode={setSourceCode} onCompile={onCompile} isRunning={isRunning} />

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14, flexWrap: 'wrap', gap: 10 }}>
          <h3 style={{ fontSize: 15.5, fontWeight: 700 }}>Recursive Descent Trace ({steps.length} steps)</h3>
          <StatusBanner ok={errors.length === 0} okText="Syntax Valid" errText={`${errors.length} Syntax/Lexical Error(s)`} />
        </div>
        <ErrorList errors={errors} />
        <div className="data-table-wrap" style={{ marginTop: 12, maxHeight: 400, overflowY: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Step</th>
                <th>Grammar Rule</th>
                <th>Action</th>
                <th>Lookahead</th>
                <th>Location</th>
              </tr>
            </thead>
            <tbody>
              {steps.map((s) => (
                <tr key={s.step}>
                  <td>{s.step}</td>
                  <td className="mono" style={{ color: 'var(--purple-dark)', fontWeight: 600 }}>{s.rule}</td>
                  <td>{s.action}</td>
                  <td className="mono"><span className="badge badge-purple">{s.lookahead}</span></td>
                  <td>L{s.line}:C{s.column}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export function ParseTreePage({ pipeline }) {
  return (
    <div>
      <PageHeader title="Parse Tree Visualization" subtitle="Interactive Concrete Parse Tree with expand/collapse and step-by-step playback." />
      <ParseTreeVisualizer tree={pipeline?.parse_tree} steps={pipeline?.parse_steps || []} />
    </div>
  );
}

export function ASTPage({ pipeline }) {
  return (
    <div>
      <PageHeader title="Abstract Syntax Tree (AST)" subtitle="Simplified structural tree of operators, operands, and control flow with JSON export." />
      <ASTVisualizer ast={pipeline?.ast} />
    </div>
  );
}

export function SemanticPage({ pipeline }) {
  const sem = pipeline?.semantic || { valid: false, symbol_table: [], errors: [], warnings: [] };
  return (
    <div>
      <PageHeader title="Semantic Analyzer & Symbol Table" subtitle="Checks variable declarations, duplicates, scopes, and static/inferred types." />

      <div className="card" style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14, flexWrap: 'wrap', gap: 10 }}>
          <h3 style={{ fontSize: 15.5, fontWeight: 700 }}>Semantic Diagnostics</h3>
          <StatusBanner ok={sem.valid} okText="Semantic Analysis Passed" errText={`${sem.errors?.length || 0} Semantic Error(s)`} />
        </div>
        <ErrorList errors={sem.errors || []} />
        {sem.warnings?.length > 0 && (
          <div style={{ marginTop: 12, padding: 12, borderRadius: 10, background: 'var(--warning-bg)', fontSize: 13 }}>
            {sem.warnings.map((w, i) => <div key={i}>• {w}</div>)}
          </div>
        )}
      </div>

      <div className="card">
        <h3 style={{ fontSize: 15.5, fontWeight: 700, marginBottom: 12 }}>Symbol Table ({sem.symbol_table?.length || 0} symbols)</h3>
        <div className="data-table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Identifier</th>
                <th>Type</th>
                <th>Scope Level</th>
                <th>Declared Line</th>
                <th>Initialized</th>
                <th>Declaration</th>
              </tr>
            </thead>
            <tbody>
              {(sem.symbol_table || []).map((sym, idx) => (
                <tr key={idx}>
                  <td className="mono" style={{ fontWeight: 700, color: 'var(--purple-dark)' }}>{sym.name}</td>
                  <td><span className="badge badge-purple">{sym.var_type}</span></td>
                  <td>{sym.scope_level}</td>
                  <td>Line {sym.line}</td>
                  <td>{sym.initialized ? <span className="badge badge-success">Yes</span> : 'No'}</td>
                  <td>{sym.implicit ? 'Implicit' : 'Explicit'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export function IntermediateCodePage({ pipeline }) {
  const tac = pipeline?.tac || [];
  return (
    <div>
      <PageHeader title="Intermediate Code Generation (TAC)" subtitle="Three-Address Code instructions lowered from the validated AST." />
      <div className="card">
        <h3 style={{ fontSize: 15.5, fontWeight: 700, marginBottom: 12 }}>Generated Three-Address Code ({tac.length} instructions)</h3>
        {!tac.length ? (
          <div className="card-lavender" style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: 28 }}>
            Compile valid source code without errors to generate Three-Address Code.
          </div>
        ) : (
          <div style={{ background: '#FCFBFF', border: '1px solid var(--border-color)', borderRadius: 12, padding: 14 }}>
            {tac.map((inst) => (
              <div key={inst.line} className="mono" style={{ display: 'flex', gap: 16, padding: '5px 8px', fontSize: 13.5, borderBottom: '1px solid #F3EFFA' }}>
                <span style={{ color: 'var(--text-secondary)', minWidth: 28 }}>{inst.line}.</span>
                <span style={{ color: 'var(--text-main)', fontWeight: 500 }}>{inst.text}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export function OptimizerPage({ pipeline }) {
  const opt = pipeline?.optimization || { original: [], optimized: [], passes_applied: [] };
  return (
    <div>
      <PageHeader title="Code Optimization" subtitle="Constant Propagation, Constant Folding, Common Subexpression Elimination, and Dead Code Elimination." />

      <div className="card" style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10, alignItems: 'center' }}>
          <Sparkles size={17} color="var(--purple-primary)" />
          <span style={{ fontWeight: 700, fontSize: 14 }}>Optimization Passes Applied:</span>
          {opt.passes_applied?.length ? (
            opt.passes_applied.map((p, i) => (
              <span key={i} className="badge badge-purple">{p.pass} ({p.changes})</span>
            ))
          ) : (
            <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>No further optimizations applicable.</span>
          )}
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <h3 style={{ fontSize: 15.5, fontWeight: 700, marginBottom: 12 }}>Original TAC ({opt.original?.length || 0} lines)</h3>
          <div style={{ background: '#FCFBFF', border: '1px solid var(--border-color)', borderRadius: 12, padding: 12 }}>
            {(opt.original || []).map((inst) => (
              <div key={inst.line} className="mono" style={{ display: 'flex', gap: 14, padding: '4px 6px', fontSize: 13 }}>
                <span style={{ color: 'var(--text-secondary)' }}>{inst.line}.</span>
                <span>{inst.text}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h3 style={{ fontSize: 15.5, fontWeight: 700, marginBottom: 12, color: 'var(--purple-dark)' }}>
            Optimized TAC ({opt.optimized?.length || 0} lines)
          </h3>
          <div style={{ background: 'var(--lavender-soft)', border: '1px solid #D6CCF0', borderRadius: 12, padding: 12 }}>
            {(opt.optimized || []).map((inst) => (
              <div key={inst.line} className="mono" style={{ display: 'flex', gap: 14, padding: '4px 6px', fontSize: 13 }}>
                <span style={{ color: 'var(--purple-primary)', fontWeight: 700 }}>{inst.line}.</span>
                <span style={{ fontWeight: 600 }}>{inst.text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export function ExecutionPage({ pipeline }) {
  const exec = pipeline?.execution || { status: 'skipped', output: [], memory: {}, steps_executed: 0, errors: [] };
  const memEntries = Object.entries(exec.memory || {});

  return (
    <div>
      <PageHeader title="Code Execution & Memory" subtitle="Safe custom AST interpreter (zero eval) with runtime error protection and live memory state." />

      <div className="grid-2">
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <h3 style={{ fontSize: 15.5, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
              <Terminal size={16} color="var(--purple-primary)" /> Program Output
            </h3>
            <StatusBanner
              ok={exec.status === 'success'}
              okText={`Executed (${exec.steps_executed} steps)`}
              errText={exec.status === 'runtime_error' ? 'Runtime Error' : 'Execution Skipped'}
            />
          </div>

          <ErrorList errors={exec.errors || []} />

          <div
            className="mono"
            style={{
              marginTop: 12,
              background: '#FCFBFF',
              border: '1px solid var(--border-color)',
              borderRadius: 12,
              padding: 16,
              minHeight: 160,
              fontSize: 13.5,
            }}
          >
            {exec.output?.length ? (
              exec.output.map((line, i) => <div key={i} style={{ padding: '2px 0' }}>&gt; {line}</div>)
            ) : (
              <span style={{ color: 'var(--text-secondary)' }}>No console output produced. Use print(...) to output values.</span>
            )}
          </div>
        </div>

        <div className="card">
          <h3 style={{ fontSize: 15.5, fontWeight: 700, marginBottom: 12 }}>Variable Memory State</h3>
          <div className="data-table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Variable</th>
                  <th>Type</th>
                  <th>Final Value</th>
                </tr>
              </thead>
              <tbody>
                {memEntries.length ? (
                  memEntries.map(([name, info]) => (
                    <tr key={name}>
                      <td className="mono" style={{ fontWeight: 700, color: 'var(--purple-dark)' }}>{name}</td>
                      <td><span className="badge badge-purple">{info.type}</span></td>
                      <td className="mono" style={{ fontWeight: 600 }}>{String(info.value)}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={3} style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>No variables in memory.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
