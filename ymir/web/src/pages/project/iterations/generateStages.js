
const matchKeywords = (dataset, project, field) => field !== 'testSet' || dataset.keywords.some(kw => project.keywords?.includes(kw))

export default (project = {}) => {
  if (!project.id) {
    return []
  }
  const datasetStages = [
    { field: 'candidateTrainSet', option: true, label: 'project.prepare.trainset', tip: 'project.add.trainset.tip', },
    { field: 'testSet', label: 'project.prepare.validationset', tip: 'project.add.testset.tip', },
    { field: 'miningSet', label: 'project.prepare.miningset', tip: 'project.add.miningset.tip', allowEmptyKeywords: true },
  ]
  const modelStage = { field: 'modelStage', label: 'project.prepare.model', tip: 'tip.task.filter.model', type: 1 }
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
