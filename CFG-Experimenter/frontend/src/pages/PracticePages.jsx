import React, { useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle2, Play, RotateCcw, XCircle } from 'lucide-react';
import { api } from '../services/api';
import { CodeEditor, ErrorList, LoadingSpinner, PageHeader } from '../components/common/UI';

export function ErrorSimulatorPage() {
  const [presets, setPresets] = useState([]);
  const [code, setCode] = useState('int a = 50;\nint b = 0;\nint result = a / b;\nprint(result);');
  const [errors, setErrors] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.getErrorPresets().then((d) => setPresets(d.presets || [])).catch(() => {});
  }, []);

  const runCheck = async (src = code) => {
    setLoading(true);
    try {
      const res = await api.runAll(src);
      setErrors(res.errors || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runCheck();
  }, []);

  return (
    <div>
      <PageHeader
        title="Compiler Error Simulator"
        subtitle="Test Lexical, Syntax, Semantic, and Runtime errors with exact line/column diagnostics and fix suggestions."
        actions={
          <button className="btn btn-primary" onClick={() => runCheck()} disabled={loading}>
            <Play size={15} /> Diagnose Code
          </button>
        }
      />

      <div className="grid-4" style={{ marginBottom: 20 }}>
        {presets.map((p) => (
          <button
            key={p.id}
            className="card card-hover"
            style={{ textAlign: 'left', cursor: 'pointer' }}
            onClick={() => {
              setCode(p.source_code);
              runCheck(p.source_code);
            }}
          >
            <span className="badge badge-error" style={{ marginBottom: 8 }}>{p.category}</span>
            <div style={{ fontWeight: 700, fontSize: 14, color: 'var(--text-main)' }}>{p.title}</div>
            <div style={{ fontSize: 12.5, color: 'var(--text-secondary)', marginTop: 4 }}>{p.description}</div>
          </button>
        ))}
      </div>

      <div className="grid-2">
        <div className="card">
          <h3 style={{ fontSize: 15.5, fontWeight: 700, marginBottom: 12 }}>Test Program</h3>
          <CodeEditor value={code} onChange={setCode} minHeight={200} />
        </div>

        <div className="card">
          <h3 style={{ fontSize: 15.5, fontWeight: 700, marginBottom: 8, display: 'flex', alignItems: 'center', gap: 8 }}>
            <AlertTriangle size={17} color="var(--purple-primary)" /> Diagnostic Output ({errors.length})
          </h3>
          {loading ? <LoadingSpinner /> : errors.length ? <ErrorList errors={errors} /> : (
            <div className="card-lavender" style={{ color: 'var(--success)', fontWeight: 600, padding: 24, textAlign: 'center' }}>
              No errors detected in this program!
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export function QuizPage() {
  const [topics, setTopics] = useState(['All']);
  const [selectedTopic, setSelectedTopic] = useState('All');
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadQuestions = async (topic = selectedTopic) => {
    setLoading(true);
    setResult(null);
    setAnswers({});
    try {
      const res = await api.getQuizQuestions(topic);
      setTopics(res.topics || ['All']);
      setQuestions(res.questions || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadQuestions('All');
  }, []);

  const handleSubmit = async () => {
    const res = await api.submitQuiz(selectedTopic, answers);
    setResult(res);
  };

  const resultMap = {};
  (result?.results || []).forEach((r) => {
    resultMap[r.question_id] = r;
  });

  return (
    <div>
      <PageHeader
        title="Interactive Compiler Quiz"
        subtitle="Test your understanding of Lexical Analysis, FIRST/FOLLOW, LL(1), ASTs, TAC, and Optimization."
        actions={
          <div style={{ display: 'flex', gap: 10 }}>
            <select
              value={selectedTopic}
              onChange={(e) => {
                setSelectedTopic(e.target.value);
                loadQuestions(e.target.value);
              }}
              style={{ padding: '8px 12px', borderRadius: 10, border: '1px solid var(--border-color)', fontSize: 13.5 }}
            >
              {topics.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
            <button className="btn btn-secondary" onClick={() => loadQuestions(selectedTopic)}>
              <RotateCcw size={15} /> Reset
            </button>
          </div>
        }
      />

      {result && (
        <div className="card-lavender" style={{ marginBottom: 20, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--purple-dark)' }}>
              Score: {result.score} / {result.total} ({result.percentage}%)
            </div>
            <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Review detailed explanations below for every question.</div>
          </div>
          <span className={`badge ${result.percentage >= 70 ? 'badge-success' : 'badge-warning'}`}>
            {result.percentage >= 70 ? 'Great Mastery!' : 'Keep Practicing'}
          </span>
        </div>
      )}

      {loading ? <LoadingSpinner label="Loading quiz..." /> : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {questions.map((q, idx) => {
            const res = resultMap[q.id];
            return (
              <div key={q.id} className="card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <span className="badge badge-purple">{q.topic}</span>
                  <span style={{ fontSize: 12, color: 'var(--text-secondary)', fontWeight: 600 }}>{q.difficulty}</span>
                </div>
                <div style={{ fontSize: 15, fontWeight: 600, marginBottom: 12 }}>
                  {idx + 1}. {q.question}
                </div>
                <div className="grid-2" style={{ gap: 10 }}>
                  {q.options.map((opt, optIdx) => {
                    const selected = answers[q.id] === optIdx;
                    const isCorrect = res && res.correct_index === optIdx;
                    const isWrong = res && selected && !res.is_correct;
                    return (
                      <button
                        key={optIdx}
                        disabled={Boolean(result)}
                        onClick={() => setAnswers((prev) => ({ ...prev, [q.id]: optIdx }))}
                        style={{
                          padding: '10px 14px',
                          borderRadius: 10,
                          textAlign: 'left',
                          cursor: result ? 'default' : 'pointer',
                          border: `1.5px solid ${
                            isCorrect ? 'var(--success)' : isWrong ? 'var(--error)' : selected ? 'var(--purple-primary)' : 'var(--border-color)'
                          }`,
                          background: isCorrect ? 'var(--success-bg)' : isWrong ? 'var(--error-bg)' : selected ? 'var(--purple-light)' : '#FFFFFF',
                          color: 'var(--text-main)',
                          fontSize: 13.5,
                          fontWeight: selected || isCorrect ? 600 : 400,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                        }}
                      >
                        <span>{opt}</span>
                        {isCorrect && <CheckCircle2 size={16} color="var(--success)" />}
                        {isWrong && <XCircle size={16} color="var(--error)" />}
                      </button>
                    );
                  })}
                </div>
                {res && (
                  <div style={{ marginTop: 12, padding: '10px 14px', borderRadius: 10, background: 'var(--lavender-soft)', fontSize: 13, color: 'var(--purple-dark)' }}>
                    <strong>Explanation:</strong> {res.explanation}
                  </div>
                )}
              </div>
            );
          })}

          {questions.length > 0 && !result && (
            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <button
                className="btn btn-primary"
                onClick={handleSubmit}
                disabled={Object.keys(answers).length === 0}
              >
                Submit Quiz ({Object.keys(answers).length}/{questions.length} answered)
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
