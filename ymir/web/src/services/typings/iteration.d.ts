type CreateParams = {
  iterationRound: number
  prevIteration: number
  projectId: number
  testSet: number
  miningSet: number
}

type UpdateParams = {
  currentStage: string
  miningSet?: number
  miningResult?: number
  labelSet?: number
  trainUpdateSet?: number
  model?: number
}

export { CreateParams, UpdateParams }
