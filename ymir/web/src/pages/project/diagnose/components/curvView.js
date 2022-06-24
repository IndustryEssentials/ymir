const CurvView = ({ tasks, datasets, models, data, filters = {} }) => {
  function generateTableSource(iou = 0) {
    const getInfo = (dataset) => ({
      id: dataset.id,
      name: `${dataset.name} ${dataset.versionName}`,
      model: dataset.task?.parameters?.model_id,
    })
    return source ? [getInfo(gt), ...datasets.map((dataset, index) => {
      const datasetSource = source[dataset.id] || {}
      const iouMetrics = datasetSource.iou_evaluations || {}
      const metrics = iouMetrics[iou] || {}
      return {
        ...getInfo(dataset),
        map: datasetSource.iou_averaged_evaluation,
        metrics,
        dataset,
      }
    })] : []
  }

  return null
}

export default CurvView
