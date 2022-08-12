
import { Result, BackendData } from "@/interface/common"
type Keywords = {
  [key: string]: number,
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
export interface DatasetGroup {
  id: number,
  name: string,
  projectId: number,
  createTime: string,
  versions?: Array<Dataset>,
}

export interface Dataset extends Result {
  keywordCount: number,
  isProtected: Boolean,
  assetCount: number,
  gt?: AnnotationsCount,
  pred?: AnnotationsCount,
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
}
