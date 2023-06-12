import { Classes } from './class'
import { Dataset, DatasetGroup } from './dataset'
import { Iteration } from './iteration'

interface Project {
  id: number
  name: string
  type: number
  typeLabel: string
  keywords: Classes
  candidateTrainSet: number
  trainSet?: DatasetGroup
  testSet?: Dataset
  miningSet?: Dataset
  testingSets?: number[]
  setCount: number
  trainSetVersion?: number
  model?: number
  modelStage?: number[]
  miningStrategy: number
  chunkSize?: number
  currentIteration?: Iteration
  round: number
  currentStep: string
  createTime: string
  updateTime: string
  description?: string
  isExample?: boolean
  hiddenDatasets: number[]
  hiddenModels: number[]
  enableIteration: boolean
  totalAssetCount: number
  datasetCount: number
  datasetProcessingCount: number
  datasetErrorCount: number
  modelCount: number
  modelProcessingCount: number
  modelErrorCount: number
  recommendImage: number
}

export { Project }
