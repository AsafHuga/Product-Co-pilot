import { useState } from 'react';
import { Upload, FileText, TrendingUp, TrendingDown, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';

// Types for API responses
interface ExecutiveSummary {
  row_count: number;
  column_count: number;
  data_mode: string;
  time_range?: {
    start: string;
    end: string;
    days: number;
  };
}

interface KPI {
  name: string;
  type: string;
  is_primary: boolean;
}

interface Trend {
  kpi: string;
  direction: string;
  change_pct: number;
}

interface ChangePoint {
  date: string;
  kpi: string;
  delta_pct: number;
  confidence: string;
}

interface Hypothesis {
  description: string;
  confidence: string;
}

interface Decision {
  decision: string;
  confidence: string;
  rationale: string;
}

interface AnalysisResults {
  executive_summary: ExecutiveSummary;
  kpis: KPI[];
  top_trends: Trend[];
  top_change_points: ChangePoint[];
  top_hypotheses: Hypothesis[];
  recommended_decisions: Decision[];
}

// API Configuration
const API_URL = 'http://localhost:8000'; // Change this to your deployed API URL

export default function MetricsAnalyzer() {
  const [file, setFile] = useState<File | null>(null);
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      if (!selectedFile.name.endsWith('.csv')) {
        setError('Please upload a CSV file');
        return;
      }
      setFile(selectedFile);
      setError(null);
      setResults(null);
    }
  };

  const analyzeFile = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_URL}/analyze/quick`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze metrics');
      console.error('Analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (confidence: string) => {
    switch (confidence.toLowerCase()) {
      case 'high':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getTrendColor = (changePct: number) => {
    if (changePct > 0) return 'text-green-600';
    if (changePct < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Product Metrics Copilot
          </h1>
          <p className="text-lg text-gray-600">
            Automated product analytics and AI-powered insights
          </p>
        </div>

        {/* File Upload Card */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors">
            <Upload className="mx-auto h-16 w-16 text-gray-400 mb-4" />

            <input
              type="file"
              id="fileInput"
              accept=".csv"
              onChange={handleFileChange}
              className="hidden"
            />

            <label
              htmlFor="fileInput"
              className="cursor-pointer inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 transition-colors"
            >
              Choose CSV File
            </label>

            <p className="mt-3 text-sm text-gray-500">
              Upload your product metrics CSV file
            </p>
          </div>

          {/* Selected File Info */}
          {file && (
            <div className="mt-6 flex items-center justify-between bg-blue-50 rounded-lg p-4">
              <div className="flex items-center">
                <FileText className="h-6 w-6 text-blue-600 mr-3" />
                <div>
                  <p className="font-medium text-gray-900">{file.name}</p>
                  <p className="text-sm text-gray-500">
                    {(file.size / 1024).toFixed(2)} KB
                  </p>
                </div>
              </div>

              <button
                onClick={analyzeFile}
                disabled={loading}
                className="px-6 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center"
              >
                {loading ? (
                  <>
                    <Loader2 className="animate-spin h-5 w-5 mr-2" />
                    Analyzing...
                  </>
                ) : (
                  'Analyze Metrics'
                )}
              </button>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mt-6 flex items-center p-4 bg-red-50 border border-red-200 rounded-lg">
              <AlertCircle className="h-5 w-5 text-red-600 mr-3" />
              <p className="text-red-800">{error}</p>
            </div>
          )}
        </div>

        {/* Results */}
        {results && (
          <div className="space-y-6 animate-fadeIn">
            {/* Executive Summary */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                <CheckCircle className="h-6 w-6 mr-2 text-green-600" />
                Executive Summary
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-1">Rows Analyzed</p>
                  <p className="text-3xl font-bold text-blue-600">
                    {results.executive_summary.row_count.toLocaleString()}
                  </p>
                </div>

                <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-1">Columns</p>
                  <p className="text-3xl font-bold text-green-600">
                    {results.executive_summary.column_count}
                  </p>
                </div>

                <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-1">Data Mode</p>
                  <p className="text-3xl font-bold text-purple-600 capitalize">
                    {results.executive_summary.data_mode}
                  </p>
                </div>
              </div>

              {results.executive_summary.time_range && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Time Range</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {results.executive_summary.time_range.start.split(' ')[0]} to{' '}
                    {results.executive_summary.time_range.end.split(' ')[0]}
                    <span className="text-sm text-gray-500 ml-2">
                      ({results.executive_summary.time_range.days} days)
                    </span>
                  </p>
                </div>
              )}
            </div>

            {/* KPIs */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                📈 Detected KPIs
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {results.kpis.map((kpi, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <span className="font-medium text-gray-900">{kpi.name}</span>
                    <div className="flex gap-2">
                      <span className="px-3 py-1 bg-blue-100 text-blue-800 text-xs font-semibold rounded-full">
                        {kpi.type}
                      </span>
                      {kpi.is_primary && (
                        <span className="px-3 py-1 bg-purple-100 text-purple-800 text-xs font-semibold rounded-full">
                          PRIMARY
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Trends */}
            {results.top_trends && results.top_trends.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">
                  📊 Top Trends
                </h2>

                <div className="space-y-3">
                  {results.top_trends.map((trend, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-4 border-2 border-gray-200 rounded-lg hover:border-blue-300 transition-colors"
                    >
                      <div className="flex items-center">
                        {trend.change_pct > 0 ? (
                          <TrendingUp className="h-5 w-5 text-green-600 mr-3" />
                        ) : (
                          <TrendingDown className="h-5 w-5 text-red-600 mr-3" />
                        )}
                        <div>
                          <p className="font-semibold text-gray-900">{trend.kpi}</p>
                          <p className="text-sm text-gray-500 capitalize">
                            {trend.direction}
                          </p>
                        </div>
                      </div>

                      <span
                        className={`px-4 py-2 font-bold text-lg rounded-lg ${
                          trend.change_pct > 0
                            ? 'bg-green-100 text-green-700'
                            : trend.change_pct < 0
                            ? 'bg-red-100 text-red-700'
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {trend.change_pct > 0 ? '+' : ''}
                        {trend.change_pct.toFixed(1)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Change Points */}
            {results.top_change_points && results.top_change_points.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">
                  🔔 Major Change Points
                </h2>

                <div className="space-y-3">
                  {results.top_change_points.map((cp, index) => (
                    <div
                      key={index}
                      className="p-4 border-l-4 border-blue-500 bg-blue-50 rounded-lg"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-semibold text-gray-900">{cp.kpi}</span>
                        <span
                          className={`px-3 py-1 text-xs font-bold rounded-full border ${getConfidenceColor(
                            cp.confidence
                          )}`}
                        >
                          {cp.confidence.toUpperCase()}
                        </span>
                      </div>
                      <p className="text-sm text-gray-700">
                        <span className="font-medium">
                          {cp.date.split(' ')[0]}
                        </span>
                        : {cp.delta_pct > 0 ? '+' : ''}
                        {cp.delta_pct.toFixed(1)}% change
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Hypotheses */}
            {results.top_hypotheses && results.top_hypotheses.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">
                  💡 Key Hypotheses
                </h2>

                <div className="space-y-4">
                  {results.top_hypotheses.map((hyp, index) => (
                    <div
                      key={index}
                      className="p-5 border-l-4 border-purple-500 bg-purple-50 rounded-lg"
                    >
                      <div className="flex items-start gap-3">
                        <span
                          className={`px-3 py-1 text-xs font-bold rounded-full ${getConfidenceColor(
                            hyp.confidence
                          )}`}
                        >
                          {hyp.confidence.toUpperCase()}
                        </span>
                        <p className="text-gray-900 flex-1">{hyp.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recommended Decisions */}
            {results.recommended_decisions &&
              results.recommended_decisions.length > 0 && (
                <div className="bg-white rounded-xl shadow-lg p-6">
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">
                    ✅ Recommended Decisions
                  </h2>

                  <div className="space-y-4">
                    {results.recommended_decisions.map((decision, index) => (
                      <div
                        key={index}
                        className={`p-6 rounded-lg border-2 ${
                          decision.confidence === 'high'
                            ? 'bg-green-50 border-green-300'
                            : decision.confidence === 'medium'
                            ? 'bg-yellow-50 border-yellow-300'
                            : 'bg-red-50 border-red-300'
                        }`}
                      >
                        <div className="flex items-center gap-3 mb-3">
                          <span
                            className={`px-3 py-1 text-sm font-bold rounded-full ${getConfidenceColor(
                              decision.confidence
                            )}`}
                          >
                            {decision.confidence.toUpperCase()}
                          </span>
                          <h3 className="text-xl font-bold text-gray-900">
                            {decision.decision}
                          </h3>
                        </div>
                        <p className="text-gray-700 leading-relaxed">
                          {decision.rationale}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
          </div>
        )}
      </div>
    </div>
  );
}
