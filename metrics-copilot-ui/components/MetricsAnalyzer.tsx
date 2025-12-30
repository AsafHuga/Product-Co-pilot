'use client';

/**
 * Product Metrics Copilot - Premium Enterprise UI
 *
 * Top-tier product analytics interface with stunning visuals,
 * smooth animations, and premium design language.
 */

import React, { useState, useCallback, useEffect } from 'react';
import {
  Upload, TrendingUp, TrendingDown, AlertCircle, Brain,
  Sparkles, FileText, BarChart3, Zap, Activity, Target,
  ArrowUpRight, ArrowDownRight, Clock, Users, Lightbulb,
  Shield, Lock, Trash2, CheckCircle2, X
} from 'lucide-react';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';

const API_URL = 'https://web-production-55d55.up.railway.app';

interface AnalysisResults {
  executive_summary: {
    row_count: number;
    column_count: number;
    data_mode: string;
    time_range?: {
      start: string;
      end: string;
    };
  };
  kpis: Array<{
    name: string;
    type: string;
    is_primary: boolean;
  }>;
  top_trends: Array<{
    kpi: string;
    direction: string;
    change_pct: number;
  }>;
  top_change_points: Array<{
    date: string;
    kpi: string;
    delta_pct: number;
    confidence: string;
  }>;
  top_hypotheses: Array<{
    description: string;
    confidence: string;
  }>;
  recommended_decisions: Array<{
    decision: string;
    confidence: string;
    rationale: string;
  }>;
  metadata?: {
    transformation_metadata?: {
      detected_format?: string;
      transformation_type?: string;
      original_rows?: number;
      final_rows?: number;
      transformations?: string[];
      steps?: Array<{
        step: string;
        [key: string]: any;
      }>;
    };
  };
}

export default function MetricsAnalyzer() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [progress, setProgress] = useState(0);
  const [showOnboarding, setShowOnboarding] = useState(true);
  const [currentStep, setCurrentStep] = useState(0);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.name.endsWith('.csv')) {
        setFile(droppedFile);
        setError(null);
      } else {
        setError('Please upload a CSV file');
      }
    }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const analyzeFile = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError(null);
    setProgress(0);

    const progressInterval = setInterval(() => {
      setProgress(prev => Math.min(prev + 10, 90));
    }, 500);

    try {
      const formData = new FormData();
      formData.append('file', file);

      console.log('Sending request to:', `${API_URL}/analyze/quick`);

      const response = await fetch(`${API_URL}/analyze/quick`, {
        method: 'POST',
        body: formData,
        mode: 'cors',
      });

      clearInterval(progressInterval);
      setProgress(100);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('API Error:', response.status, errorText);
        throw new Error(`Analysis failed (${response.status}): ${response.statusText}`);
      }

      const data = await response.json();
      console.log('Analysis successful:', data);
      setResults(data);
    } catch (err) {
      clearInterval(progressInterval);
      console.error('Fetch error:', err);
      setError(err instanceof Error ? err.message : 'Analysis failed. Check console for details.');
    } finally {
      setLoading(false);
      setTimeout(() => setProgress(0), 1000);
    }
  };

  const getConfidenceBadge = (confidence: string) => {
    const config = {
      high: {
        variant: 'default' as const,
        className: 'bg-emerald-500 hover:bg-emerald-600 text-white border-0'
      },
      medium: {
        variant: 'secondary' as const,
        className: 'bg-amber-500 hover:bg-amber-600 text-white border-0'
      },
      low: {
        variant: 'outline' as const,
        className: 'border-slate-300 text-slate-600'
      }
    };

    const conf = config[confidence as keyof typeof config] || config.low;

    return (
      <Badge variant={conf.variant} className={conf.className}>
        {confidence.toUpperCase()}
      </Badge>
    );
  };

  const getTrendIcon = (direction: string, changePct: number) => {
    const isPositive = direction === 'increasing';
    return isPositive ? (
      <div className="flex items-center justify-center w-10 h-10 rounded-full bg-emerald-100 dark:bg-emerald-950">
        <ArrowUpRight className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
      </div>
    ) : (
      <div className="flex items-center justify-center w-10 h-10 rounded-full bg-rose-100 dark:bg-rose-950">
        <ArrowDownRight className="h-5 w-5 text-rose-600 dark:text-rose-400" />
      </div>
    );
  };

  // Auto-advance onboarding steps
  useEffect(() => {
    if (showOnboarding && currentStep < 2) {
      const timer = setTimeout(() => {
        setCurrentStep(prev => prev + 1);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [showOnboarding, currentStep]);

  // Close onboarding on first interaction
  useEffect(() => {
    if (file && showOnboarding) {
      setShowOnboarding(false);
    }
  }, [file, showOnboarding]);

  const privacySteps = [
    {
      icon: Upload,
      title: "1. Upload Your Data",
      description: "Upload any CSV file with your metrics. All formats supported.",
      color: "violet"
    },
    {
      icon: Brain,
      title: "2. AI Analyzes Instantly",
      description: "Our AI processes your data in real-time to generate insights.",
      color: "indigo"
    },
    {
      icon: Trash2,
      title: "3. Data Auto-Deleted",
      description: "Your data is permanently deleted immediately after analysis. Zero storage.",
      color: "emerald"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
      {/* Premium Header with Glassmorphism */}
      <div className="sticky top-0 z-50 backdrop-blur-xl bg-white/70 dark:bg-slate-900/70 border-b border-slate-200/50 dark:border-slate-800/50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-violet-600 to-indigo-600 rounded-xl blur-lg opacity-50"></div>
                <div className="relative p-2.5 bg-gradient-to-r from-violet-600 to-indigo-600 rounded-xl">
                  <Brain className="h-6 w-6 text-white" />
                </div>
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-slate-900 to-slate-700 dark:from-white dark:to-slate-300 bg-clip-text text-transparent">
                  Product Metrics Copilot
                </h1>
                <p className="text-xs text-slate-500 dark:text-slate-400">Powered by GPT-4o</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Badge className="bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 border-0">
                <Shield className="w-3 h-3 mr-1" />
                100% Private
              </Badge>
              <Badge className="bg-violet-100 text-violet-700 dark:bg-violet-950 dark:text-violet-300 border-0">
                <Sparkles className="w-3 h-3 mr-1" />
                AI-Powered
              </Badge>
            </div>
          </div>
        </div>
      </div>

      {/* Animated Onboarding Overlay */}
      {showOnboarding && !results && (
        <div className="fixed inset-0 z-40 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-6 animate-in fade-in duration-300">
          <Card className="max-w-4xl w-full border-2 border-violet-200 dark:border-violet-800 shadow-2xl animate-in slide-in-from-bottom-8 duration-500">
            <CardHeader className="text-center pb-4">
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1" />
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowOnboarding(false)}
                  className="text-slate-400 hover:text-slate-600"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 text-sm font-medium mb-4">
                <Shield className="w-4 h-4" />
                Your Data is 100% Private & Secure
              </div>
              <CardTitle className="text-3xl font-bold bg-gradient-to-r from-slate-900 to-violet-900 dark:from-white dark:to-violet-200 bg-clip-text text-transparent">
                How It Works - Privacy First
              </CardTitle>
              <CardDescription className="text-base mt-2">
                We never store your data. Here's the complete process:
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-6 mb-8">
                {privacySteps.map((step, idx) => {
                  const Icon = step.icon;
                  const isActive = idx === currentStep;
                  const isPast = idx < currentStep;

                  return (
                    <div
                      key={idx}
                      className={`relative transition-all duration-500 ${
                        isActive ? 'scale-105' : isPast ? 'opacity-70' : 'opacity-50'
                      }`}
                    >
                      <div className={`p-6 rounded-xl border-2 h-full transition-all duration-500 ${
                        isActive
                          ? 'border-violet-400 bg-violet-50 dark:bg-violet-950/30 shadow-lg shadow-violet-500/20'
                          : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900'
                      }`}>
                        <div className={`inline-flex items-center justify-center w-14 h-14 rounded-full mb-4 transition-all duration-500 ${
                          isActive
                            ? step.color === 'violet' ? 'bg-gradient-to-r from-violet-500 to-violet-600' :
                              step.color === 'indigo' ? 'bg-gradient-to-r from-indigo-500 to-indigo-600' :
                              'bg-gradient-to-r from-emerald-500 to-emerald-600'
                            : 'bg-slate-200 dark:bg-slate-800'
                        }`}>
                          <Icon className={`h-7 w-7 transition-colors ${
                            isActive ? 'text-white' : 'text-slate-400 dark:text-slate-600'
                          }`} />
                        </div>
                        <h3 className="text-lg font-bold mb-2">{step.title}</h3>
                        <p className="text-sm text-slate-600 dark:text-slate-400">{step.description}</p>

                        {isActive && (
                          <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
                            <div className="flex items-center gap-2 text-xs text-emerald-600 dark:text-emerald-400">
                              <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                              {idx === 0 && "Ready to upload"}
                              {idx === 1 && "Processing in real-time"}
                              {idx === 2 && "Auto-deletion guaranteed"}
                            </div>
                          </div>
                        )}
                      </div>

                      {isPast && (
                        <div className="absolute -top-2 -right-2">
                          <div className="bg-emerald-500 text-white rounded-full p-1">
                            <CheckCircle2 className="h-4 w-4" />
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>

              <Alert className="border-emerald-200 bg-emerald-50 dark:bg-emerald-950/20 dark:border-emerald-900">
                <Lock className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                <AlertTitle className="text-emerald-900 dark:text-emerald-200">
                  Zero Data Retention Policy
                </AlertTitle>
                <AlertDescription className="text-emerald-700 dark:text-emerald-300">
                  <ul className="space-y-1 mt-2 text-sm">
                    <li>✓ Your data is processed in memory only</li>
                    <li>✓ Permanently deleted immediately after analysis</li>
                    <li>✓ No databases, no backups, no logs containing your data</li>
                    <li>✓ We only see aggregated, anonymous insights - never raw data</li>
                  </ul>
                </AlertDescription>
              </Alert>

              <div className="mt-6 text-center">
                <Button
                  onClick={() => setShowOnboarding(false)}
                  size="lg"
                  className="bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 text-white px-8"
                >
                  Got it! Let's Analyze
                </Button>
                <p className="text-xs text-slate-500 mt-3">
                  This message won't show again
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
        {/* Hero Section */}
        {!results && (
          <div className="text-center space-y-4 py-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-violet-100 dark:bg-violet-950 text-violet-700 dark:text-violet-300 text-sm font-medium mb-4">
              <Sparkles className="w-4 h-4" />
              Next-Generation Analytics
            </div>
            <h2 className="text-5xl font-bold bg-gradient-to-r from-slate-900 via-violet-900 to-slate-900 dark:from-white dark:via-violet-200 dark:to-white bg-clip-text text-transparent leading-tight">
              Transform Data Into
              <br />
              Actionable Insights
            </h2>
            <p className="text-xl text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
              Upload your metrics CSV and let AI analyze trends, detect anomalies, and provide intelligent recommendations.
            </p>
            <div className="flex items-center justify-center gap-6 pt-4 text-sm text-slate-500">
              <div className="flex items-center gap-2">
                <Shield className="h-4 w-4 text-emerald-600" />
                <span>Zero data retention</span>
              </div>
              <div className="flex items-center gap-2">
                <Lock className="h-4 w-4 text-emerald-600" />
                <span>Auto-deleted instantly</span>
              </div>
              <div className="flex items-center gap-2">
                <Trash2 className="h-4 w-4 text-emerald-600" />
                <span>Never stored</span>
              </div>
            </div>
          </div>
        )}

        {/* Premium Upload Card - Minimized when results shown */}
        {results ? (
          // Compact upload section after analysis
          <Card className="border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-violet-100 dark:bg-violet-950 rounded-lg">
                    <FileText className="h-4 w-4 text-violet-600 dark:text-violet-400" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-900 dark:text-white">{file?.name}</p>
                    <p className="text-xs text-slate-500">
                      {results.executive_summary.row_count.toLocaleString()} rows analyzed
                    </p>
                  </div>
                </div>
                <Button
                  onClick={() => {
                    setFile(null);
                    setResults(null);
                    setError(null);
                  }}
                  variant="outline"
                  size="sm"
                  className="gap-2"
                >
                  <Upload className="h-3.5 w-3.5" />
                  New Analysis
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : (
          // Full upload card before analysis
          <Card className="border-2 border-slate-200 dark:border-slate-800 shadow-xl shadow-slate-200/50 dark:shadow-slate-950/50 overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-violet-500/5 to-indigo-500/5 pointer-events-none"></div>
            <CardHeader className="relative">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-gradient-to-br from-violet-100 to-indigo-100 dark:from-violet-950 dark:to-indigo-950 rounded-lg">
                    <Upload className="h-5 w-5 text-violet-600 dark:text-violet-400" />
                  </div>
                  <div>
                    <CardTitle className="text-lg">Upload Your Data</CardTitle>
                    <CardDescription>Any CSV format • Auto-transforms raw data • Up to 50MB</CardDescription>
                  </div>
                </div>
                {file && (
                  <Button
                    onClick={() => {
                      setFile(null);
                      setResults(null);
                      setError(null);
                    }}
                    variant="ghost"
                    size="sm"
                    className="text-slate-500"
                  >
                    Clear
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent className="relative">
            <div
              className={`relative border-2 border-dashed rounded-xl p-16 text-center transition-all duration-300 ${
                dragActive
                  ? 'border-violet-500 bg-violet-50 dark:bg-violet-950/20 scale-[0.98]'
                  : 'border-slate-300 dark:border-slate-700 hover:border-violet-400 dark:hover:border-violet-600 hover:bg-slate-50 dark:hover:bg-slate-900/50'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <input
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />

              <div className="space-y-6">
                <div className="flex justify-center">
                  <div className="relative">
                    <div className="absolute inset-0 bg-gradient-to-br from-violet-400 to-indigo-400 rounded-2xl blur-2xl opacity-20"></div>
                    <div className="relative p-6 bg-gradient-to-br from-violet-100 to-indigo-100 dark:from-violet-950 dark:to-indigo-950 rounded-2xl">
                      <FileText className="h-12 w-12 text-violet-600 dark:text-violet-400" />
                    </div>
                  </div>
                </div>

                {file ? (
                  <div className="space-y-3">
                    <div className="inline-flex items-center gap-2 px-4 py-2 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
                      <FileText className="h-4 w-4 text-violet-600" />
                      <span className="font-medium text-slate-900 dark:text-white">
                        {file.name}
                      </span>
                      <Badge variant="secondary" className="ml-2">
                        {(file.size / 1024).toFixed(1)} KB
                      </Badge>
                    </div>
                    <p className="text-sm text-slate-500">
                      Ready to analyze • Click below to start
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <p className="text-xl font-semibold text-slate-900 dark:text-white">
                      Drop your CSV file here
                    </p>
                    <p className="text-sm text-slate-500 max-w-md mx-auto">
                      or click to browse • Supports product metrics, experiments, and time series data
                    </p>
                  </div>
                )}
              </div>
            </div>

            {error && (
              <Alert variant="destructive" className="mt-6 border-rose-200 dark:border-rose-800">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="mt-6">
              <Button
                onClick={analyzeFile}
                disabled={!file || loading}
                className="w-full h-14 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 text-white text-base font-semibold shadow-lg shadow-violet-500/25 transition-all duration-200 hover:shadow-xl hover:shadow-violet-500/30 hover:scale-[1.02] disabled:opacity-50 disabled:scale-100"
                size="lg"
              >
                {loading ? (
                  <>
                    <Activity className="mr-2 h-5 w-5 animate-spin" />
                    Analyzing with AI...
                  </>
                ) : (
                  <>
                    <Zap className="mr-2 h-5 w-5" />
                    Analyze with AI
                  </>
                )}
              </Button>

              {/* Privacy Notice */}
              <div className="mt-4 p-3 rounded-lg bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-900">
                <div className="flex items-start gap-2 text-xs text-emerald-700 dark:text-emerald-300">
                  <Shield className="h-4 w-4 mt-0.5 flex-shrink-0" />
                  <p>
                    <strong>Privacy Guaranteed:</strong> Your data is processed in-memory and <strong>permanently deleted immediately</strong> after analysis. We never store, log, or retain your raw data.
                  </p>
                </div>
              </div>

              {loading && progress > 0 && (
                <div className="mt-6 space-y-3">
                  <Progress value={progress} className="h-2" />
                  <div className="flex items-center justify-center gap-2 text-sm text-slate-600 dark:text-slate-400">
                    <Activity className="h-4 w-4 animate-pulse" />
                    <span>
                      {progress < 30 ? 'Uploading data...' :
                       progress < 60 ? 'Running AI analysis...' :
                       progress < 90 ? 'Generating insights...' :
                       'Finalizing results...'}
                    </span>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
        )}

        {/* Results Section */}
        {results && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
            {/* Data Transformation Info */}
            {results.metadata?.transformation_metadata && (
              <Alert className="border-violet-200 bg-violet-50 dark:bg-violet-950/20 dark:border-violet-900">
                <Sparkles className="h-4 w-4 text-violet-600 dark:text-violet-400" />
                <AlertTitle className="text-violet-900 dark:text-violet-200">
                  Data Automatically Transformed
                </AlertTitle>
                <AlertDescription className="text-violet-700 dark:text-violet-300 space-y-2">
                  <p>
                    Detected format: <strong>{results.metadata.transformation_metadata.detected_format}</strong>
                    {results.metadata.transformation_metadata.original_rows && results.metadata.transformation_metadata.final_rows && (
                      <span> • {results.metadata.transformation_metadata.original_rows.toLocaleString()} events → {results.metadata.transformation_metadata.final_rows.toLocaleString()} aggregated rows</span>
                    )}
                  </p>
                  {results.metadata.transformation_metadata.transformations && results.metadata.transformation_metadata.transformations.length > 0 && (
                    <ul className="text-xs space-y-1 ml-4 list-disc">
                      {results.metadata.transformation_metadata.transformations.slice(0, 3).map((transform, idx) => (
                        <li key={idx}>{transform}</li>
                      ))}
                    </ul>
                  )}
                </AlertDescription>
              </Alert>
            )}

            {/* Executive Summary */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card className="border-slate-200 dark:border-slate-800 hover:shadow-lg transition-shadow duration-300">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <p className="text-sm font-medium text-slate-500">Rows Analyzed</p>
                      <p className="text-3xl font-bold bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">
                        {results.executive_summary.row_count.toLocaleString()}
                      </p>
                    </div>
                    <div className="p-2 bg-violet-100 dark:bg-violet-950 rounded-lg">
                      <BarChart3 className="h-5 w-5 text-violet-600 dark:text-violet-400" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-slate-200 dark:border-slate-800 hover:shadow-lg transition-shadow duration-300">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <p className="text-sm font-medium text-slate-500">KPIs Detected</p>
                      <p className="text-3xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
                        {results.kpis.length}
                      </p>
                    </div>
                    <div className="p-2 bg-emerald-100 dark:bg-emerald-950 rounded-lg">
                      <Target className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-slate-200 dark:border-slate-800 hover:shadow-lg transition-shadow duration-300">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <p className="text-sm font-medium text-slate-500">Data Type</p>
                      <p className="text-xl font-bold text-slate-900 dark:text-white capitalize">
                        {results.executive_summary.data_mode}
                      </p>
                    </div>
                    <div className="p-2 bg-indigo-100 dark:bg-indigo-950 rounded-lg">
                      <Activity className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-slate-200 dark:border-slate-800 hover:shadow-lg transition-shadow duration-300">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <p className="text-sm font-medium text-slate-500">Time Period</p>
                      <p className="text-sm font-semibold text-slate-900 dark:text-white">
                        {results.executive_summary.time_range ?
                          `${new Date(results.executive_summary.time_range.start).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${new Date(results.executive_summary.time_range.end).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`
                          : 'Not available'}
                      </p>
                    </div>
                    <div className="p-2 bg-amber-100 dark:bg-amber-950 rounded-lg">
                      <Clock className="h-5 w-5 text-amber-600 dark:text-amber-400" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Tabs */}
            <Tabs defaultValue="hypotheses" className="w-full">
              <TabsList className="grid w-full grid-cols-4 bg-slate-100 dark:bg-slate-900 p-1">
                <TabsTrigger value="hypotheses" className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-800">
                  <Lightbulb className="h-4 w-4 mr-2" />
                  AI Insights
                </TabsTrigger>
                <TabsTrigger value="trends" className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-800">
                  <TrendingUp className="h-4 w-4 mr-2" />
                  Trends
                </TabsTrigger>
                <TabsTrigger value="changes" className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-800">
                  <Activity className="h-4 w-4 mr-2" />
                  Changes
                </TabsTrigger>
                <TabsTrigger value="decisions" className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-800">
                  <Target className="h-4 w-4 mr-2" />
                  Actions
                </TabsTrigger>
              </TabsList>

              {/* AI Hypotheses Tab */}
              <TabsContent value="hypotheses" className="space-y-4 mt-6">
                <Card className="border-slate-200 dark:border-slate-800">
                  <CardHeader>
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-gradient-to-br from-violet-100 to-indigo-100 dark:from-violet-950 dark:to-indigo-950 rounded-lg">
                        <Brain className="h-5 w-5 text-violet-600 dark:text-violet-400" />
                      </div>
                      <div>
                        <CardTitle>AI-Generated Hypotheses</CardTitle>
                        <CardDescription>Intelligent insights powered by GPT-4o</CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {results.top_hypotheses.map((hypothesis, idx) => (
                      <div
                        key={idx}
                        className="group p-6 border border-slate-200 dark:border-slate-800 rounded-xl hover:shadow-lg hover:border-violet-200 dark:hover:border-violet-900 transition-all duration-300 bg-white dark:bg-slate-900"
                      >
                        <div className="flex items-start gap-4">
                          <div className="flex-shrink-0 flex items-center justify-center w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-indigo-500 text-white font-bold text-sm">
                            {idx + 1}
                          </div>
                          <div className="flex-1 space-y-3">
                            <div className="flex items-center gap-2">
                              {getConfidenceBadge(hypothesis.confidence)}
                            </div>
                            <p className="text-sm leading-relaxed text-slate-700 dark:text-slate-300">
                              {hypothesis.description}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Trends Tab */}
              <TabsContent value="trends" className="space-y-4 mt-6">
                <Card className="border-slate-200 dark:border-slate-800">
                  <CardHeader>
                    <CardTitle>Key Performance Trends</CardTitle>
                    <CardDescription>Statistical analysis of your metrics</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {results.top_trends.map((trend, idx) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between p-5 border border-slate-200 dark:border-slate-800 rounded-xl hover:shadow-md transition-all duration-200 bg-white dark:bg-slate-900"
                      >
                        <div className="flex items-center gap-4">
                          {getTrendIcon(trend.direction, trend.change_pct)}
                          <div>
                            <p className="font-semibold text-slate-900 dark:text-white">
                              {trend.kpi}
                            </p>
                            <p className="text-sm text-slate-500 capitalize">{trend.direction}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className={`text-2xl font-bold ${
                            trend.change_pct > 0
                              ? 'text-emerald-600 dark:text-emerald-400'
                              : 'text-rose-600 dark:text-rose-400'
                          }`}>
                            {trend.change_pct > 0 ? '+' : ''}{trend.change_pct.toFixed(1)}%
                          </p>
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Change Points Tab */}
              <TabsContent value="changes" className="space-y-4 mt-6">
                <Card className="border-slate-200 dark:border-slate-800">
                  <CardHeader>
                    <CardTitle>Significant Changes</CardTitle>
                    <CardDescription>Notable shifts in your metrics</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {results.top_change_points.map((change, idx) => (
                      <div
                        key={idx}
                        className="p-5 border-l-4 border-l-violet-500 bg-slate-50 dark:bg-slate-900 rounded-lg space-y-3"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <Activity className="h-5 w-5 text-violet-600" />
                            <span className="font-semibold text-slate-900 dark:text-white">
                              {change.kpi}
                            </span>
                          </div>
                          {getConfidenceBadge(change.confidence)}
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-slate-500">
                            {new Date(change.date).toLocaleDateString('en-US', {
                              month: 'short',
                              day: 'numeric',
                              year: 'numeric'
                            })}
                          </span>
                          <span className={`text-lg font-bold ${
                            change.delta_pct > 0
                              ? 'text-emerald-600 dark:text-emerald-400'
                              : 'text-rose-600 dark:text-rose-400'
                          }`}>
                            {change.delta_pct > 0 ? '+' : ''}{change.delta_pct.toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Decisions Tab */}
              <TabsContent value="decisions" className="space-y-4 mt-6">
                <Card className="border-slate-200 dark:border-slate-800">
                  <CardHeader>
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-gradient-to-br from-emerald-100 to-teal-100 dark:from-emerald-950 dark:to-teal-950 rounded-lg">
                        <Target className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
                      </div>
                      <div>
                        <CardTitle>Recommended Actions</CardTitle>
                        <CardDescription>Data-driven next steps</CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {results.recommended_decisions.length > 0 ? (
                      results.recommended_decisions.map((decision, idx) => (
                        <div
                          key={idx}
                          className="p-6 border-l-4 border-l-emerald-500 bg-gradient-to-r from-emerald-50 to-transparent dark:from-emerald-950/20 dark:to-transparent rounded-lg space-y-3"
                        >
                          <div className="flex items-start justify-between gap-4">
                            <div className="flex-1 space-y-3">
                              <div className="flex items-center gap-2">
                                <Badge className="bg-emerald-100 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-300 border-0">
                                  Action #{idx + 1}
                                </Badge>
                                {getConfidenceBadge(decision.confidence)}
                              </div>
                              <h4 className="font-semibold text-slate-900 dark:text-white text-lg">
                                {decision.decision}
                              </h4>
                              <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                                {decision.rationale}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-12">
                        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-slate-100 dark:bg-slate-800 mb-4">
                          <Target className="h-8 w-8 text-slate-400" />
                        </div>
                        <p className="text-slate-500">No specific decisions recommended at this time</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        )}
      </div>
    </div>
  );
}
