
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
  nagetiveCount?: number,
  projectNagetiveCount?: number,
  assetCount: number,
  ignoredKeywords: Array<string>,
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