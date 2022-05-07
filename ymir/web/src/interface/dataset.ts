
import { Result } from "@/interface/common"
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
