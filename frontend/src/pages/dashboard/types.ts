export const METHOD_LABELS: Record<string, string> = {
  M1: 'M1: TF-IDF + LogReg',
  M2: 'M2: Zero-Shot LLM',
  M3: 'M3: RAG Combined',
  M4: 'M4: RAG Decoupled (IFSI)',
};

export const COMPARISON_LABELS: Record<string, string> = {
  M2_vs_M3__clean: 'M2 vs M3 (Clean)',
  M2_vs_M3__marked: 'M2 vs M3 (Marked Attack)',
  M2_vs_M3__unmarked: 'M2 vs M3 (Unmarked Attack)',
  marked_vs_unmarked__M1: 'M1 (Marked vs Unmarked)',
  marked_vs_unmarked__M2: 'M2 (Marked vs Unmarked)',
  marked_vs_unmarked__M3: 'M3 (Marked vs Unmarked)',
  marked_vs_unmarked__M4: 'M4 (Marked vs Unmarked)',
  combined_vs_decoupled_M3_vs_M4__clean: 'M3 vs M4 (Clean)',
  combined_vs_decoupled_M3_vs_M4__marked: 'M3 vs M4 (Marked Attack)',
  combined_vs_decoupled_M3_vs_M4__unmarked: 'M3 vs M4 (Unmarked Attack)',
};

export interface MetricTableRow {
  id: string;
  method: string;
  methodCode: string;
  model: string;
  condition: string;
  sampleSize: string;
  sampleCount: number;
  accuracy: number;
  recall: number;
  fpr: number;
  precision: number;
  f1: number;
  invalidRate: number;
  latencySeconds: number;
  latencyDisplay: string;
}

export type SortField =
  | 'method'
  | 'condition'
  | 'model'
  | 'accuracy'
  | 'recall'
  | 'fpr'
  | 'precision'
  | 'f1'
  | 'latencySeconds';

export const PILOT_ROWS: MetricTableRow[] = [
  {
    id: 'pilot_m2_clean_llama',
    method: METHOD_LABELS['M2'],
    methodCode: 'M2',
    model: 'llama3.2:3b',
    condition: 'Clean',
    sampleSize: 'Pilot N=50',
    sampleCount: 50,
    accuracy: 0.940,
    recall: 0.882,
    fpr: 0.030,
    precision: 0.938,
    f1: 0.909,
    invalidRate: 0.0,
    latencySeconds: 1.150,
    latencyDisplay: '1.150 s',
  },
  {
    id: 'pilot_m2_unmarked_llama',
    method: METHOD_LABELS['M2'],
    methodCode: 'M2',
    model: 'llama3.2:3b',
    condition: 'Unmarked',
    sampleSize: 'Pilot N=50',
    sampleCount: 50,
    accuracy: 0.440,
    recall: 0.235,
    fpr: 0.455,
    precision: 0.211,
    f1: 0.222,
    invalidRate: 0.0,
    latencySeconds: 1.190,
    latencyDisplay: '1.190 s',
  },
  {
    id: 'pilot_m3_unmarked_llama',
    method: METHOD_LABELS['M3'],
    methodCode: 'M3',
    model: 'llama3.2:3b',
    condition: 'Unmarked',
    sampleSize: 'Pilot N=50',
    sampleCount: 50,
    accuracy: 0.380,
    recall: 0.176,
    fpr: 0.515,
    precision: 0.158,
    f1: 0.167,
    invalidRate: 0.0,
    latencySeconds: 2.140,
    latencyDisplay: '2.140 s',
  },
  {
    id: 'pilot_m4_unmarked_llama',
    method: METHOD_LABELS['M4'],
    methodCode: 'M4',
    model: 'llama3.2:3b',
    condition: 'Unmarked',
    sampleSize: 'Pilot N=50',
    sampleCount: 50,
    accuracy: 0.720,
    recall: 0.941,
    fpr: 0.394,
    precision: 0.552,
    f1: 0.696,
    invalidRate: 0.0,
    latencySeconds: 2.650,
    latencyDisplay: '2.650 s',
  },
];
