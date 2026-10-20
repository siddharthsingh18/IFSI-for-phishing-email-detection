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
  specificity: number;
  f1: number;
  invalidRate: number;
  latencySeconds: number;
  latencyDisplay: string;
  tp: number;
  fp: number;
  tn: number;
  fn: number;
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
    specificity: 0.970,
    f1: 0.909,
    invalidRate: 0.0,
    latencySeconds: 1.150,
    latencyDisplay: '1.150 s',
    tp: 15,
    fp: 1,
    tn: 32,
    fn: 2,
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
    specificity: 0.545,
    f1: 0.222,
    invalidRate: 0.0,
    latencySeconds: 1.190,
    latencyDisplay: '1.190 s',
    tp: 4,
    fp: 15,
    tn: 18,
    fn: 13,
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
    specificity: 0.485,
    f1: 0.167,
    invalidRate: 0.0,
    latencySeconds: 2.140,
    latencyDisplay: '2.140 s',
    tp: 3,
    fp: 17,
    tn: 16,
    fn: 14,
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
    specificity: 0.606,
    f1: 0.696,
    invalidRate: 0.0,
    latencySeconds: 2.790,
    latencyDisplay: '2.790 s',
    tp: 16,
    fp: 13,
    tn: 20,
    fn: 1,
  },
];

export interface GroupedBarPair {
  id: string;
  methodCode: string;
  methodLabel: string;
  methodFullName: string;
  condition: string;
  recallPct: number;
  fprPct: number;
  accuracyPct: number;
  f1: number;
  model: string;
  sampleSize: string;
  isGroupStart: boolean;
  isGroupCenter: boolean;
  isGroupEnd: boolean;
  groupIndex: number;
  groupLength: number;
  methodIndex: number;
}

export function buildGroupedChartData(
  allRows: MetricTableRow[],
  filterMethod: string,
  filterCondition: string,
  filterModel: string
): GroupedBarPair[] {
  const methodKeys = filterMethod === 'all' ? ['M1', 'M2', 'M3', 'M4'] : [filterMethod];
  const conditions =
    filterCondition === 'all'
      ? ['Clean', 'Marked', 'Unmarked']
      : [filterCondition.charAt(0).toUpperCase() + filterCondition.slice(1).toLowerCase()];

  const shortMethodNames: Record<string, string> = {
    M1: 'M1: TF-IDF',
    M2: 'M2: Zero-Shot',
    M3: 'M3: RAG Comb.',
    M4: 'M4: IFSI',
  };

  const results: GroupedBarPair[] = [];

  methodKeys.forEach((mKey, methodIdx) => {
    const methodItems: GroupedBarPair[] = [];

    conditions.forEach((cond) => {
      const matchingRows = allRows.filter((r) => {
        if (r.methodCode !== mKey) return false;
        if (r.condition.toLowerCase() !== cond.toLowerCase()) return false;
        if (filterModel !== 'all') {
          if (filterModel === 'qwen' && !r.model.includes('qwen')) return false;
          if (filterModel === 'llama' && !r.model.includes('llama')) return false;
          if (filterModel === 'tfidf' && !r.model.includes('TF-IDF')) return false;
        }
        return true;
      });

      if (matchingRows.length === 0) return;

      let chosenRow = matchingRows[0];
      if (filterModel === 'all') {
        const fullRow = matchingRows.find((r) => r.sampleSize === 'N=522');
        if (fullRow) chosenRow = fullRow;
      }

      methodItems.push({
        id: `${mKey}_${cond}`,
        methodCode: mKey,
        methodLabel: shortMethodNames[mKey] || mKey,
        methodFullName: METHOD_LABELS[mKey] || mKey,
        condition: cond,
        recallPct: Number((chosenRow.recall * 100).toFixed(1)),
        fprPct: Number((chosenRow.fpr * 100).toFixed(1)),
        accuracyPct: Number((chosenRow.accuracy * 100).toFixed(1)),
        f1: chosenRow.f1,
        model: chosenRow.model,
        sampleSize: chosenRow.sampleSize,
        isGroupStart: false,
        isGroupCenter: false,
        isGroupEnd: false,
        groupIndex: 0,
        groupLength: 0,
        methodIndex: methodIdx,
      });
    });

    const groupLen = methodItems.length;
    if (groupLen > 0) {
      const centerIdx = Math.floor(groupLen / 2);
      methodItems.forEach((item, idx) => {
        item.groupIndex = idx;
        item.groupLength = groupLen;
        item.isGroupStart = idx === 0;
        item.isGroupCenter = idx === centerIdx;
        item.isGroupEnd = idx === groupLen - 1;
        results.push(item);
      });
    }
  });

  return results;
}

