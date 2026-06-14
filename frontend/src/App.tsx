import React, { useState } from 'react';
import axios from 'axios';
import { Search, Zap, Shield, Database, BarChart2, CheckCircle, XCircle } from 'lucide-react';

const API_BASE = 'http://localhost:8000/api';

interface RAGResponse {
  answer: str;
  sources: string[];
  chunks: string[];
}

interface EvalResult {
  question: string;
  basic: RAGResponse;
  advanced: RAGResponse;
  evaluation: {
    winner: string;
    reasoning: string;
    scores: { A: number; B: number };
  };
}

function App() {
  const [question, setQuestion] = useState('');
  const [basicRes, setBasicRes] = useState<RAGResponse | null>(null);
  const [advRes, setAdvRes] = useState<RAGResponse | null>(null);
  const [evalResults, setEvalResults] = useState<EvalResult[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [ingesting, setIngesting] = useState(false);

  const handleQuery = async () => {
    if (!question) return;
    setLoading(true);
    try {
      const [b, a] = await Promise.all([
        axios.post(`${API_BASE}/query/basic`, { question }),
        axios.post(`${API_BASE}/query/advanced`, { question })
      ]);
      setBasicRes(b.data);
      setAdvRes(a.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleIngest = async () => {
    setIngesting(true);
    try {
      await axios.post(`${API_BASE}/ingest`, { mode: 'advanced' });
      alert('Ingestion complete!');
    } catch (err) {
      console.error(err);
    } finally {
      setIngesting(false);
    }
  };

  const handleEvaluate = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/evaluate`);
      setEvalResults(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-8 font-sans">
      <header className="max-w-6xl mx-auto mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Corpmind RAG Dashboard</h1>
          <p className="text-slate-500 text-sm">Comparing Basic vs Advanced Retrieval-Augmented Generation</p>
        </div>
        <div className="space-x-4">
          <button 
            onClick={handleIngest}
            disabled={ingesting}
            className="px-4 py-2 bg-slate-800 text-white rounded-lg hover:bg-slate-700 disabled:opacity-50 text-sm transition"
          >
            {ingesting ? 'Ingesting...' : 'Run Ingestion'}
          </button>
          <button 
            onClick={handleEvaluate}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-500 text-sm transition"
          >
            Run Benchmarks
          </button>
        </div>
      </header>

      <main className="max-w-6xl mx-auto">
        <div className="bg-white p-6 rounded-xl shadow-sm mb-8">
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-3 text-slate-400 size-5" />
              <input 
                type="text"
                placeholder="Ask a corporate question..."
                className="w-full pl-10 pr-4 py-3 bg-slate-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleQuery()}
              />
            </div>
            <button 
              onClick={handleQuery}
              disabled={loading}
              className="px-8 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-500 disabled:opacity-50 font-medium transition"
            >
              {loading ? 'Thinking...' : 'Search'}
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Basic RAG Panel */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="bg-slate-50 p-4 border-b border-slate-200 flex items-center gap-2">
              <Zap className="size-5 text-amber-500" />
              <h2 className="font-semibold text-slate-800">Basic RAG</h2>
              <span className="text-[10px] bg-slate-200 px-2 py-0.5 rounded text-slate-600 uppercase font-bold tracking-wider">Top-K Vector</span>
            </div>
            <div className="p-6">
              {basicRes ? (
                <div className="space-y-4">
                  <p className="text-slate-700 leading-relaxed">{basicRes.answer}</p>
                  <div className="pt-4 border-t border-slate-100">
                    <h3 className="text-xs font-bold text-slate-400 uppercase mb-2">Sources</h3>
                    <div className="flex flex-wrap gap-2">
                      {basicRes.sources.map((s, i) => (
                        <span key={i} className="text-[11px] bg-slate-100 px-2 py-1 rounded text-slate-600">{s}</span>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="py-12 text-center text-slate-400 italic">No query performed yet</div>
              )}
            </div>
          </div>

          {/* Advanced RAG Panel */}
          <div className="bg-white rounded-xl shadow-sm border border-indigo-100 overflow-hidden ring-1 ring-indigo-500 ring-opacity-10">
            <div className="bg-indigo-50 p-4 border-b border-indigo-100 flex items-center gap-2">
              <Shield className="size-5 text-indigo-600" />
              <h2 className="font-semibold text-slate-800">Advanced RAG</h2>
              <span className="text-[10px] bg-indigo-600 px-2 py-0.5 rounded text-white uppercase font-bold tracking-wider">LangGraph + Neo4j</span>
            </div>
            <div className="p-6">
              {advRes ? (
                <div className="space-y-4">
                  <p className="text-slate-700 leading-relaxed">{advRes.answer}</p>
                  <div className="pt-4 border-t border-slate-100">
                    <h3 className="text-xs font-bold text-slate-400 uppercase mb-2">Graph + Vector Sources</h3>
                    <div className="flex flex-wrap gap-2">
                      {advRes.sources.map((s, i) => (
                        <span key={i} className="text-[11px] bg-indigo-50 px-2 py-1 rounded text-indigo-600 border border-indigo-100">{s}</span>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="py-12 text-center text-slate-400 italic">No query performed yet</div>
              )}
            </div>
          </div>
        </div>

        {/* Evaluation Benchmarks */}
        {evalResults && (
          <div className="mt-12 bg-white rounded-xl shadow-sm border border-slate-200 p-8">
            <div className="flex items-center gap-2 mb-6">
              <BarChart2 className="size-6 text-indigo-600" />
              <h2 className="text-xl font-bold text-slate-900">Evaluation Benchmarks</h2>
            </div>
            <div className="space-y-6">
              {evalResults.map((res, i) => (
                <div key={i} className="border border-slate-100 rounded-lg p-6 bg-slate-50/50">
                  <h3 className="font-semibold text-slate-800 mb-4">Q: {res.question}</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div className="text-sm bg-white p-3 rounded border border-slate-100">
                      <span className="text-[10px] font-bold text-slate-400 uppercase block mb-1">Basic</span>
                      {res.basic.answer.substring(0, 150)}...
                    </div>
                    <div className="text-sm bg-white p-3 rounded border border-indigo-100">
                      <span className="text-[10px] font-bold text-indigo-400 uppercase block mb-1">Advanced</span>
                      {res.advanced.answer.substring(0, 150)}...
                    </div>
                  </div>
                  <div className={`p-4 rounded-lg flex items-start gap-3 ${res.evaluation.winner === 'B' ? 'bg-green-50 border border-green-100' : 'bg-slate-100'}`}>
                    {res.evaluation.winner === 'B' ? <CheckCircle className="size-5 text-green-600 shrink-0 mt-0.5" /> : <BarChart2 className="size-5 text-slate-600 shrink-0 mt-0.5" />}
                    <div>
                      <span className="font-bold text-sm block">Winner: {res.evaluation.winner === 'B' ? 'Advanced RAG' : res.evaluation.winner === 'A' ? 'Basic RAG' : 'Draw'}</span>
                      <p className="text-xs text-slate-600 mt-1 leading-relaxed">{res.evaluation.reasoning}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
