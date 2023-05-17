enum TaskResultType {
  dataset = 1,
  model = 2,
  prediction = 3,
  image = 4,
}

const isImage = (type: number) => TaskResultType.image === type
const isDataset = (type: TaskResultType) => TaskResultType.dataset === type
const isModel = (type: TaskResultType) => TaskResultType.model === type
const isPrediction = (type: TaskResultType) => TaskResultType.prediction === type

export { TaskResultType, isImage, isDataset, isModel, isPrediction }
