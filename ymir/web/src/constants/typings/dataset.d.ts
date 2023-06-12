import { Types } from '@/components/dataset/add/AddTypes'
import { IMPORTSTRATEGY } from '../dataset'
import { Classes, ClassesCount } from './class'
import { Group, Result } from './common'

interface DatasetGroup extends Group {
  versions?: Array<Dataset>
}

interface Dataset extends Result {
  groupId: number
  keywordCount: number
  isProtected: Boolean
  assetCount: number
  gt?: AnnotationsCount
  cks?: CKCounts
  tags?: CKCounts
  evaluated?: boolean
  suggestions: DatasetSuggestions
}
type Suggestion = {
  bounding: number
  values: string[]
  type?: string
}
type DatasetSuggestions = {
  [key: string]: Suggestion
}

type KeywordCountsType = { [key: string]: number }
type CKItem = { keyword: string; count: number; children?: CKItem[] }
type CKCounts = {
  keywords: CKItem[]
  counts: KeywordCountsType
  subKeywordsTotal: number
  total: KeywordCountsType
}
type AnnotationsCount = {
  count: ClassesCount
  keywords: Classes
  negative: number
  total: number
}

interface DatasetAnalysis extends Dataset {
  keywordCounts: AnalysisChart
  assetHWRatio: AnalysisChart
  assetArea: AnalysisChart
  assetQuality: AnalysisChart
  total: number
  negative: number
  average: number
  totalArea: number
  quality: AnalysisChart
  areaRatio: AnalysisChart
  keywordAnnotationCount: AnalysisChart
  keywordArea: AnalysisChart
  instanceArea: AnalysisChart
  crowdedness: AnalysisChart
  complexity: AnalysisChart
}

type AnalysisChartData = {
  x: number | string
  y: number
}
type AnalysisChart = {
  data: AnalysisChartData[]
  total?: number
}

type ImportingItem = {
  index?: number
  type: Types
  name: string
  source: string | number
  sourceName: string
  strategy?: IMPORTSTRATEGY
  classes?: string[]
  dup?: false
}

export {
  DatasetGroup,
  Dataset,
  Suggestion,
  DatasetSuggestions,
  AnnotationsCount,
  DatasetAnalysis,
  KeywordCountsType,
  AnalysisChartData,
  AnalysisChart,
  CKItem,
  CKCounts,
  ImportingItem,
}
