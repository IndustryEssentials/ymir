
import { Result, BackendData, Group } from "@/interface/common"
import { ModelVersion } from "./model"
type Keywords = {
  [key: string]: number,
}
type CK = {
  [key: string]: any,
}
type AnnotationsCount = {
  count: Keywords,
  keywords: Array<string>,
  negative: number,
  total: number,
}
type AnylysisAnnotation = {
  keywords: Keywords,
  total: number,
  average: number,
  negative: number,
  quality: Array<BackendData>,
  area: Array<BackendData>,
  areaRatio: Array<BackendData>,
}
export interface DatasetGroup extends Group {
  versions?: Array<Dataset>,
}

export interface Dataset extends Result {
  keywordCount: number,
  isProtected: Boolean,
  assetCount: number,
  gt?: AnnotationsCount,
  pred?: AnnotationsCount,
  inferClass?: Array<string>,
  cks?: BackendData,
  tags?: BackendData,
}

export interface InferDataset extends Dataset {
  modelId?: number,
  model?: ModelVersion,
  validationDatasetId?: number,
  validationDataset?: Dataset,
}

export interface DatasetAnalysis {
  name: string,
  version: number,
  versionName: string,
  assetCount: number,
  totalAssetMbytes: number,
  assetBytes: Array<BackendData>,
  assetHWRatio: Array<BackendData>,
  assetArea: Array<BackendData>,
  assetQuality: Array<BackendData>,
  gt: AnylysisAnnotation,
  pred: AnylysisAnnotation,
  inferClass?: Array<string>,
  cks?: BackendData,
  tags?: BackendData,
}

export interface Asset {
  id: number,
  hash: string,
  keywords: Array<string>,
  url: string,
  metadata?: {
    width: number,
    height: number,
    channel: number,
  },
  size?: number,
  annotations: Array<Annotation>,
  evaluated?: boolean,
  cks?: CK,
}

export interface Annotation {
  keyword: string,
  box: {
    x: number,
    y: number,
    w: number,
    h: number,
    rotate_angle: number,
  }
  color?: string,
  score?: number,
  gt?: boolean,
  cm: number,
  tags?: CK,
}
