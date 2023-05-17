type PlainObject = {
  [key: string]: any
}

interface Iteration {
  id: number
  projectId: number
  name?: string
  round: number
  currentStep?: Step
  steps: Step[]
  testSet: number
  wholeMiningSet: number
  prevIteration?: number
  model?: number
  end: boolean
}

interface Step {
  id: number
  finished?: boolean
  name: string
  percent?: number
  preSetting?: PlainObject
  state?: number
  taskId?: number
  taskType?: number
  resultType?: 'dataset' | 'model'
  resultId?: number
}

type KeywordsCount = {
  keywords: string[]
  count: {
    [keyword: string]: number
  }
}
type MiningStats = {
  totalList: KeywordsCount
  keywordList: KeywordsCount
}

export { Iteration, Step, MiningStats }
