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
 *   {number}  [miningDataset]
 *   {number}  [miningResult]
 *   {number}  [labelResult]
 *   {number}  traningDataset
 *   {number}  trainingModel
 *   {number}  prevTrainingDataset
 *   {number}  projectId
 * }
 * @returns
 */
export function createIterations({
  name,
  currentStage,
  iterationRound,
  miningDataset,
  miningResult,
  labelResult,
  traningDataset,
  trainingModel,
  prevTrainingDataset,
  projectId,
}) {
  return request.post("/iterations/", {
    name,
    current_stage: currentStage,
    iteration_round: iterationRound,
    mining_input_dataset_id: miningDataset,
    mining_output_dataset_id: miningResult,
    label_output_dataset_id: labelResult,
    training_input_dataset_id: traningDataset,
    training_output_model_id: trainingModel,
    previous_training_dataset_id: prevTrainingDataset,
    project_id: projectId,
  })
}
/**
 * update iteration stage
 * @param {object} iteration
 * {
 *   {number}  [currentStage]
 *   {number}  [miningDataset]
 *   {number}  [miningResult]
 *   {number}  [labelResult]
 *   {number}  traningDataset
 *   {number}  trainingModel
 *   {number}  prevTrainingDataset
 * }
 * @returns
 */
export function updateIteration(
  id,
  {
    currentStage,
    miningDataset,
    miningResult,
    labelResult,
    traningDataset,
    trainingModel,
    prevTrainingDataset,
  }
) {
  return request({
    method: "patch",
    url: `/iterations/${id}`,
    data: {
      current_stage: currentStage,
      mining_input_dataset_id: miningDataset,
      mining_output_dataset_id: miningResult,
      label_output_dataset_id: labelResult,
      training_input_dataset_id: traningDataset,
      training_output_model_id: trainingModel,
      previous_training_dataset_id: prevTrainingDataset,
    },
  })
}
