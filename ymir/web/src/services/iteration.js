import request from "@/utils/request"

/** iteration service */
/**
 * get iteration by id
 * @param {number} project_id project id
 * @param {number} id iteration id
 * @returns
 */
export function getIteration(project_id, id) {
  return request.get(`iterations/${id}`, { params: { project_id }})
}

/**
 * get project iterations by id
 * @param {number} id
 * @returns
 */
export function getIterations(id) {
  return request.get(`iterations/`, { params: { project_id: id } })
}

/**
 * create a iteration
 * @param {object} iteration
 * {
 *   {string}  [name]
 *   {number}  [currentStage]
 *   {number}  iterationRound
 *   {number}  prevTrainingDataset
 *   {number}  projectId
 *   {number}  testSet
 * }
 * @returns
 */
export function createIteration({
  name,
  currentStage,
  iterationRound,
  prevIteration,
  projectId,
  testSet,
}) {
  return request.post("/iterations/", {
    name,
    current_stage: currentStage,
    iteration_round: iterationRound,
    project_id: projectId,
    previous_iteration: prevIteration,
    testing_dataset_id: testSet,
  })
}
/**
 * update iteration stage
 * @param {object} iteration
 * {
 *   {number}  [currentStage]
 *   {number}  [trainUpdateSet]
 *   {number}  [miningSet]
 *   {number}  [miningResult]
 *   {number}  [labelSet]
 *   {number}  [model]
 * }
 * @returns
 */
export function updateIteration(
  id,
  {
    currentStage,
    miningSet,
    miningResult,
    labelSet,
    trainUpdateSet,
    model,
  }
) {
  return request({
    method: "patch",
    url: `/iterations/${id}`,
    data: {
      current_stage: currentStage,
      mining_input_dataset_id: miningSet,
      mining_output_dataset_id: miningResult,
      label_output_dataset_id: labelSet,
      training_input_dataset_id: trainUpdateSet,
      training_output_model_id: model,
    },
  })
}
