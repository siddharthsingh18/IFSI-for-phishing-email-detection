/**
 * IFSI Phishing Email Detection & Prompt Injection Benchmark - API Client
 *
 * Strongly-typed API client wrapper for all FastAPI backend endpoints.
 * Base URL defaults to http://localhost:8000 (overrideable via VITE_API_BASE_URL).
 */

const getApiBaseUrl = (): string => {
  try {
    const metaEnv = (import.meta as unknown as { env?: { VITE_API_BASE_URL?: string } })?.env;
    if (metaEnv?.VITE_API_BASE_URL) {
      return metaEnv.VITE_API_BASE_URL.replace(/\/+$/, '');
    }
  } catch {
    // Ignore in non-ESM or non-Vite runtimes
  }

  try {
    const globalProc =
      typeof globalThis !== 'undefined'
        ? (globalThis as unknown as { process?: { env?: Record<string, string> } }).process
        : undefined;
    if (globalProc?.env?.VITE_API_BASE_URL) {
      return globalProc.env.VITE_API_BASE_URL.replace(/\/+$/, '');
    }
  } catch {
    // Ignore in browser runtimes
  }

  return 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();

// =========================================================================
// TypeScript Interfaces & Types
// =========================================================================

export interface OllamaHealth {
  connected: boolean;
  status: 'online' | 'offline' | string;
  api_base: string;
  available_models: string[];
  message: string;
}

export interface FaissHealth {
  loaded: boolean;
  status: 'loaded' | 'not_loaded' | string;
  index_path: string;
  index_size: number;
  message: string;
}

export interface EnvironmentHealth {
  python_version: string;
  package: string;
}

export interface HealthResponse {
  status: 'ok' | 'degraded' | string;
  ollama: OllamaHealth;
  faiss: FaissHealth;
  environment: EnvironmentHealth;
}

export interface ClassifyRequest {
  text: string;
  subject?: string;
  sender?: string;
  method?: 'M1' | 'M2' | 'M3' | 'M4' | string;
  model?: string;
  k?: number;
}

export interface ClassifyCompareRequest {
  text: string;
  subject?: string;
  sender?: string;
  model?: string;
  k?: number;
  include_archived?: boolean;
}

export interface ClassificationResult {
  method: string;
  verdict: 'phishing' | 'legitimate' | string;
  is_phishing: boolean;
  confidence: number;
  has_prompt_injection: boolean;
  has_prompt_injection_display: string;
  phishing_verdict?: 'phishing' | 'legitimate' | 'error' | string;
  injection_verdict?: 'detected' | 'clean' | 'error' | string;
  security_action?: 'allow' | 'quarantine_review' | 'block' | 'manual_review' | string;
  latency_ms: number;
  latency_seconds: number;
  reasons: string[];
  is_valid: boolean;
  failure_type?: string | null;
  failure_message?: string | null;
  attempts?: number;
  raw_response?: string | null;
  raw_response_call1?: string | null;
  raw_response_call2?: string | null;
  retrieved_samples?: Array<Record<string, unknown>> | null;
  has_injection?: boolean | null;
  is_phishing_only?: boolean | null;
  injection_spans?: Array<{
    start: number;
    end: number;
    source: 'model' | 'pattern';
    text: string;
  }>;
}

export interface ModelCatalogEntry {
  id: string;
  label: string;
  role: string;
  description: string;
  artifact: string;
  artifact_complete: boolean;
}

export interface ModelCatalog {
  primary_model: string;
  available_models: ModelCatalogEntry[];
  benchmarks: Record<string, Record<string, unknown>>;
}

export interface MethodStyle {
  card_class: string;
  badge_html: string;
  status_label: string;
  note: string;
}

export interface ConsensusEvaluation {
  has_disagreement: boolean;
  num_phishing: number;
  num_legitimate: number;
  majority_verdict: string;
  summary_title: string;
  summary_detail: string;
  method_styles: Record<string, MethodStyle>;
}

export interface CompareResponse {
  results: ClassificationResult[];
  by_method: Record<string, ClassificationResult>;
  consensus: ConsensusEvaluation;
}

export interface InjectRequest {
  text: string;
  style?: 'marked' | 'unmarked' | string;
  attack_family?:
    | 'label_override'
    | 'false_authority'
    | 'output_hijack'
    | 'rule_redefinition'
    | 'light_obfuscation'
    | string;
  position?: 'body_start' | 'body_middle' | 'body_end' | 'prepend' | 'middle' | 'append' | string;
}

export interface InjectResponse {
  injected_text: string;
  payload: string;
  style: string;
  attack_family: string;
  position: string;
}

export interface MistakeRecord {
  method: string;
  condition: string;
  model: string;
  id: string;
  true_label: string;
  predicted_label: string;
  confidence: number;
  snippet: string;
}

export interface ConfusionMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  specificity: number;
  f1: number;
  fpr: number;
  true_positives: number;
  false_positives: number;
  true_negatives: number;
  false_negatives: number;
  invalid_count: number;
  invalid_rate: number;
  total_samples: number;
  valid_count: number;
  mean_latency_seconds: number;
  total_runtime_seconds: number;
  [key: string]: unknown;
}

export interface ConfusionCellResponse {
  cell_key: string;
  method: string;
  condition: string;
  confusion_matrix?: {
    tp: number;
    fp: number;
    tn: number;
    fn: number;
  };
  metrics: ConfusionMetrics;
  bootstrap_95_ci?: Record<string, [number, number]> | null;
}

export interface McNemarTestResult {
  'a_correct_b_wrong (b)': number;
  'a_wrong_b_correct (c)': number;
  both_correct: number;
  both_incorrect: number;
  discordant_pairs: number;
  mcnemar_chi2: number;
  p_value: number;
  paired_samples: number;
  significant_alpha_0_05: boolean;
  raw_p_value: number;
  holm_bonferroni_rank: number;
  holm_bonferroni_factor: number;
  holm_bonferroni_p_value: number;
  significant_after_holm_bonferroni: boolean;
  [key: string]: unknown;
}

export interface McNemarTableRow {
  rank: number;
  comparison: string;
  discordant_b: number;
  discordant_c: number;
  raw_p_value: number;
  holm_bonferroni_factor: number;
  holm_bonferroni_p_value: number;
  significant_after_holm_bonferroni: boolean;
}

export interface McNemarResponse {
  description: string;
  num_tests: number;
  tests: Record<string, McNemarTestResult>;
  table?: McNemarTableRow[];
}

export interface BenchmarkSummary {
  cells: Record<string, {
    condition: string;
    method: string;
    metrics: ConfusionMetrics;
    bootstrap_95_ci?: Record<string, [number, number]>;
  }>;
  paired_tests: Record<string, McNemarTestResult>;
  dataset?: {
    total_emails: number;
    train_size: number;
    val_size: number;
    test_size: number;
    test_phishing?: number;
    test_legitimate?: number;
    marked_injections: number;
    unmarked_injections: number;
    total_injections: number;
  };
  pilot_comparison?: Record<string, unknown>;
  manifest?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface ReportResponse {
  filename: string;
  report: string;
  markdown?: string;
  content_length?: number;
}

export interface AttackFamilyExample {
  marked: {
    injected_text: string;
    base_instruction?: string;
    attack_template_id?: string;
  };
  unmarked_by_style: Record<string, Array<{
    injected_text: string;
    base_instruction?: string;
    attack_template_id?: string;
    attack_position?: string;
  }>>;
}

export interface PresetSample {
  subject: string;
  sender: string;
  body: string;
  label: 'phishing' | 'legitimate' | string;
  condition: 'clean' | 'marked' | 'unmarked' | string;
}

// =========================================================================
// API Fetch Error Handler
// =========================================================================

export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(status: number, message: string, detail?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${path.startsWith('/') ? path : `/${path}`}`;
  const headers = new Headers(options.headers || {});

  if (!headers.has('Content-Type') && options.body && typeof options.body === 'string') {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail: unknown;
    try {
      errorDetail = await response.json();
    } catch {
      errorDetail = await response.text();
    }
    const message =
      typeof errorDetail === 'object' && errorDetail !== null && 'detail' in errorDetail
        ? String((errorDetail as { detail: unknown }).detail)
        : `API request failed with HTTP ${response.status}: ${response.statusText}`;
    throw new ApiError(response.status, message, errorDetail);
  }

  // Handle plain text response (e.g. raw markdown report)
  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('text/plain') || contentType.includes('text/markdown')) {
    return (await response.text()) as unknown as T;
  }

  return response.json() as Promise<T>;
}

// =========================================================================
// Typed API Endpoints Client
// =========================================================================

export const apiClient = {
  /**
   * Base URL currently configured for the client
   */
  baseUrl: API_BASE_URL,

  /**
   * GET /health - Check Ollama, FAISS index, and runtime environment
   */
  async getHealth(): Promise<HealthResponse> {
    return request<HealthResponse>('/health');
  },

  async getModels(): Promise<ModelCatalog> {
    return request<ModelCatalog>('/models');
  },

  /**
   * POST /classify - Classify email with single architecture (M1-M4)
   */
  async classifyEmail(req: ClassifyRequest): Promise<ClassificationResult> {
    return request<ClassificationResult>('/classify', {
      method: 'POST',
      body: JSON.stringify({
        text: req.text,
        subject: req.subject || '',
        sender: req.sender || '',
        method: req.method || 'M1',
        model: req.model,
        k: req.k ?? 3,
      }),
    });
  },

  /**
   * POST /classify/compare - Classify email across ALL methods M1-M4 + compute consensus
   */
  async classifyCompare(req: ClassifyCompareRequest): Promise<CompareResponse> {
    return request<CompareResponse>('/classify/compare', {
      method: 'POST',
      body: JSON.stringify({
        text: req.text,
        subject: req.subject || '',
        sender: req.sender || '',
        model: req.model,
        k: req.k ?? 3,
      }),
    });
  },

  /**
   * POST /inject - Synthesize marked or unmarked injection attack payload
   */
  async injectEmail(req: InjectRequest): Promise<InjectResponse> {
    return request<InjectResponse>('/inject', {
      method: 'POST',
      body: JSON.stringify({
        text: req.text,
        style: req.style || 'unmarked',
        attack_family: req.attack_family || 'label_override',
        position: req.position || 'body_start',
      }),
    });
  },

  /**
   * GET /results/summary - Full benchmark summary JSON
   */
  async getBenchmarkSummary(): Promise<BenchmarkSummary> {
    return request<BenchmarkSummary>('/results/summary');
  },

  /**
   * GET /results/mistakes - Retrieve worst high-confidence misclassifications
   */
  async getWorstMistakes(params?: {
    method?: string;
    limit?: number;
  }): Promise<MistakeRecord[]> {
    const searchParams = new URLSearchParams();
    if (params?.method) searchParams.append('method', params.method);
    if (params?.limit !== undefined) searchParams.append('limit', String(params.limit));
    const qs = searchParams.toString();
    return request<MistakeRecord[]>(`/results/mistakes${qs ? `?${qs}` : ''}`);
  },

  /**
   * GET /results/confusion - Single confusion matrix cell and metrics
   */
  async getConfusionCell(params?: {
    method?: string;
    condition?: string;
  }): Promise<ConfusionCellResponse> {
    const searchParams = new URLSearchParams();
    if (params?.method) searchParams.append('method', params.method);
    if (params?.condition) searchParams.append('condition', params.condition);
    const qs = searchParams.toString();
    return request<ConfusionCellResponse>(`/results/confusion${qs ? `?${qs}` : ''}`);
  },

  /**
   * GET /results/mcnemar - Paired hypothesis test table with Holm-Bonferroni correction
   */
  async getMcNemarResults(): Promise<McNemarResponse> {
    return request<McNemarResponse>('/results/mcnemar');
  },

  /**
   * GET /results/report - Report markdown (as JSON or raw text)
   */
  async getReport(raw?: boolean): Promise<ReportResponse | string> {
    const path = raw ? '/results/report?raw=true' : '/results/report';
    return request<ReportResponse | string>(path);
  },

  /**
   * GET /injections/examples - Attack family example pairs
   */
  async getInjectionExamples(params?: {
    family?: string;
    style?: string;
  }): Promise<Record<string, AttackFamilyExample> | AttackFamilyExample> {
    const searchParams = new URLSearchParams();
    if (params?.family) searchParams.append('family', params.family);
    if (params?.style) searchParams.append('style', params.style);
    const qs = searchParams.toString();
    return request<Record<string, AttackFamilyExample> | AttackFamilyExample>(
      `/injections/examples${qs ? `?${qs}` : ''}`
    );
  },

  /**
   * GET /presets - Curated preset samples for testing
   */
  async getPresets(): Promise<Record<string, PresetSample>> {
    return request<Record<string, PresetSample>>('/presets');
  },
};

export default apiClient;
