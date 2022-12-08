
export default () => {
  const datasetStages = [
    { field: 'candidateTrainSet', option: true, label: 'project.prepare.trainset', tip: 'project.add.trainset.tip', },
    { field: 'testSet', label: 'project.prepare.validationset', tip: 'project.add.testset.tip', },
    { field: 'miningSet', label: 'project.prepare.miningset', tip: 'project.add.miningset.tip', },
  ]

  const modelStage = {
    field: 'modelStage',
    label: 'project.prepare.model',
    tip: 'tip.task.filter.model',
    type: 1,
    filter: x => x,
  }

  const generateFilters = (field) => {
    return (datasets, project) => {
    const notTestingSet = (did) => !(project.testingSets || []).includes(did)
    const excludeSelected = (currentField, dataset, project) => {
      const excludeCurrent = datasetStages.filter(({ type, field }) => !type && field !== currentField)
      const ids = excludeCurrent.map(({ field }) => project[field]?.id || project[field])
      return !ids.includes(dataset.id)
    }
      return datasets.filter(dataset =>
        notTestingSet(dataset.id) &&
        excludeSelected(field, dataset, project)
        && dataset.assetCount
      )
    }
  }
  return [
    ...datasetStages.map((item) => ({ ...item, filter: generateFilters(item.field) })),
    modelStage,
  ]
}
