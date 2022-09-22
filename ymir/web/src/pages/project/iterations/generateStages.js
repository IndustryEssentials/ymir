
import { validDataset } from '@/constants/dataset'

const matchKeywords = (dataset, project, field) => field === 'miningSet' || dataset.keywords.some(kw => project.keywords?.includes(kw))

export default (project = {}, results) => {
  if (!project.id) {
    return []
  }
  const datasetStages = [
    { field: 'candidateTrainSet', option: true, label: 'project.prepare.trainset', tip: 'project.add.trainset.tip', },
    { field: 'testSet', label: 'project.prepare.validationset', tip: 'project.add.testset.tip', },
    { field: 'miningSet', label: 'project.prepare.miningset', tip: 'project.add.miningset.tip', },
  ]
  let trainValid = [
    results?.candidateTrainSet,
    results?.testSet,
  ].reduce((prev, curr) => prev && validDataset(curr), true)

  const modelStage = {
    field: 'modelStage',
    label: 'project.prepare.model',
    tip: 'tip.task.filter.model',
    type: 1,
    filter: x => x,
    trainValid,
  }

  const generateFilters = (field, project) => {
    const notTestingSet = (did) => !(project.testingSets || []).includes(did)
    const excludeSelected = (currentField, dataset, project) => {
      const excludeCurrent = datasetStages.filter(({ type, field }) => !type && field !== currentField)
      const ids = excludeCurrent.map(({ field }) => project[field]?.id || project[field])
      return !ids.includes(dataset.id)
    }
    return (datasets, project) => {
      return datasets.filter(dataset =>
        matchKeywords(dataset, project, field) &&
        notTestingSet(dataset.id) &&
        excludeSelected(field, dataset, project)
      )
    }
  }
  return [
    ...datasetStages.map((item) => ({ ...item, filter: generateFilters(item.field, project) })),
    modelStage,
  ]
}
