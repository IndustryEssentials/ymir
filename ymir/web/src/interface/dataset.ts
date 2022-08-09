
import { Result, BackendData } from "@/interface/common"
type Keywords = {
  [key: string]: number,
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
  keywordsCount: Keywords,
  isProtected: Boolean,
  nagetiveCount?: {
    gt: number,
    pred: number,
  },
  assetCount: number,
}

export interface DatasetAnalysis {
  name: string,
  version: number,
  versionName: string,
  assetCount: number,
  totalAssetMbytes: number,
  annosCnt: number,
  aveAnnosCnt: number,
  positiveAssetCnt: number,
  negativeAssetCnt: number,
  assetBytes: Array<BackendData>,
  assetHWRatio: Array<BackendData>,
  assetArea: Array<BackendData>,
  assetQuality: Array<BackendData>,
  annoAreaRatio: Array<BackendData>,
  annoQuality: Array<BackendData>,
  classNamesCount: BackendData,
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
