import React, { useCallback, useEffect, useState } from 'react';
import { AnimatePresence, MotionConfig, motion } from 'framer-motion';
import MainLayout from './layouts/MainLayout';
import DashboardPage from './pages/DashboardPage';
import { FirstFollowPage, GrammarEditorPage, LL1ParsingPage } from './pages/GrammarModulePages';
import {
  ASTPage,
  ExecutionPage,
  IntermediateCodePage,
  LexerPage,
  OptimizerPage,
  ParseTreePage,
  SemanticPage,
  SyntaxPage,
} from './pages/CompilerPipelinePages';
import { ErrorSimulatorPage, QuizPage } from './pages/PracticePages';
import { api } from './services/api';

const DEFAULT_SOURCE = `a = 10;
b = 20;
c = a + b * 2;
d = a + b * 2;
print(c);`;

const DEFAULT_GRAMMAR = `E -> T E'
E' -> + T E' | - T E' | ε
T -> F T'
T' -> * F T' | / F T' | ε
F -> ( E ) | id | num`;

export default function App() {
  const [activePage, setActivePage] = useState('dashboard');
  const [sourceCode, setSourceCode] = useState(DEFAULT_SOURCE);
  const [grammarText, setGrammarText] = useState(DEFAULT_GRAMMAR);
  const [sampleInput, setSampleInput] = useState('id + num * id');
  const [pipeline, setPipeline] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [toast, setToast] = useState(null);

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3200);
  };

  const handleRunAll = useCallback(async (codeToRun = sourceCode) => {
    setIsRunning(true);
    try {
      const res = await api.runAll(codeToRun);
      setPipeline(res);
      if (res.success) {
        showToast('Compilation & execution succeeded!', 'success');
      } else {
        showToast(`Completed with ${res.errors?.length || 1} error(s).`, 'error');
      }
    } catch (e) {
      showToast(e.message || 'Backend connection failed.', 'error');
    } finally {
      setIsRunning(false);
    }
  }, [sourceCode]);

  useEffect(() => {
    handleRunAll(DEFAULT_SOURCE);
  }, []);

  const handleNavigate = (pageId) => {
    setActivePage(pageId);
    if (pageId !== 'dashboard') {
      api.markProgress(pageId, true).catch(() => {});
    }
  };

  const handleSaveExperiment = async () => {
    const title = window.prompt('Enter a title for this experiment:', 'Compiler Experiment');
    if (!title) return;
    try {
      await api.saveExperiment({
        title,
        source_code: sourceCode,
        grammar_text: grammarText,
        status: pipeline?.success ? 'compiled' : 'draft',
      });
      showToast('Experiment saved to SQLite database!', 'success');
    } catch (e) {
      showToast('Failed to save experiment.', 'error');
    }
  };

  const handleLoadExperiment = (exp) => {
    setSourceCode(exp.source_code || DEFAULT_SOURCE);
    if (exp.grammar_text) setGrammarText(exp.grammar_text);
    handleRunAll(exp.source_code || DEFAULT_SOURCE);
    setActivePage('lexer');
    showToast(`Loaded "${exp.title}"`, 'success');
  };

  const renderPage = () => {
    switch (activePage) {
      case 'dashboard':
        return <DashboardPage onNavigate={handleNavigate} onLoadExperiment={handleLoadExperiment} />;
      case 'grammar':
        return (
          <GrammarEditorPage
            grammarText={grammarText}
            setGrammarText={setGrammarText}
            sampleInput={sampleInput}
            setSampleInput={setSampleInput}
          />
        );
      case 'first_follow':
        return <FirstFollowPage grammarText={grammarText} />;
      case 'll1_table':
        return <LL1ParsingPage grammarText={grammarText} sampleInput={sampleInput} setSampleInput={setSampleInput} />;
      case 'lexer':
        return <LexerPage sourceCode={sourceCode} setSourceCode={setSourceCode} pipeline={pipeline} onCompile={() => handleRunAll()} isRunning={isRunning} />;
      case 'syntax':
        return <SyntaxPage sourceCode={sourceCode} setSourceCode={setSourceCode} pipeline={pipeline} onCompile={() => handleRunAll()} isRunning={isRunning} />;
      case 'parse_tree':
        return <ParseTreePage pipeline={pipeline} />;
      case 'ast':
        return <ASTPage pipeline={pipeline} />;
      case 'semantic':
        return <SemanticPage pipeline={pipeline} />;
      case 'intermediate':
        return <IntermediateCodePage pipeline={pipeline} />;
      case 'optimizer':
        return <OptimizerPage pipeline={pipeline} />;
      case 'execution':
        return <ExecutionPage pipeline={pipeline} />;
      case 'errors':
        return <ErrorSimulatorPage />;
      case 'quiz':
        return <QuizPage />;
      default:
        return <DashboardPage onNavigate={handleNavigate} onLoadExperiment={handleLoadExperiment} />;
    }
  };

  return (
    <MotionConfig reducedMotion="user">
      <MainLayout
        activePage={activePage}
        onNavigate={handleNavigate}
        onRunAll={() => handleRunAll()}
        onSaveExperiment={handleSaveExperiment}
        isRunning={isRunning}
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={activePage}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.18 }}
          >
            {renderPage()}
          </motion.div>
        </AnimatePresence>

        {toast && (
          <div
            style={{
              position: 'fixed',
              bottom: 24,
              right: 24,
              zIndex: 100,
              padding: '12px 18px',
              borderRadius: 12,
              background: toast.type === 'error' ? 'var(--error)' : 'var(--purple-dark)',
              color: '#FFFFFF',
              fontWeight: 600,
              fontSize: 13.5,
              boxShadow: 'var(--shadow-lg)',
            }}
          >
            {toast.msg}
          </div>
        )}
      </MainLayout>
    </MotionConfig>
  );
}
