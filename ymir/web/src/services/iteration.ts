import request from "@/utils/request"

type CreateParams = {
  iterationRound: number
  prevIteration: number
  projectId: number
  testSet: number
  miningSet: number
}

function post(id: number, data: any, url = "") {
  return request.post(`/iterations/${id}/${url}`, data)
}

function get(id: number, params: any, url = "") {
  return request.get(`/iterations/${id}/${url}`, { params })
}

/** iteration service */
/**
 * @description get iteration by id
 * @export
 * @param {number} pid project id
 * @param {number} id  iteration id
 * @return
 */
export function getIteration(pid: number, id: number) {
  return get(id, { project_id: pid })
}

/**
 * @description get project iterations by id
 * @export
 * @param {number} pid project id
 * @return
 */
export function getIterations(pid: number) {
  return request.get(`iterations/`, { params: { project_id: pid } })
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
  iterationRound,
  prevIteration,
  projectId,
  testSet,
  miningSet,
}: CreateParams) {
  return request.post("/iterations/", {
    iteration_round: iterationRound,
    project_id: projectId,
    previous_iteration: prevIteration,
    validation_dataset_id: testSet,
    mining_dataset_id: miningSet,
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
  id: number,
  {
    currentStage,
    miningSet,
    miningResult,
    labelSet,
    trainUpdateSet,
    model,
  }: { [key: string]: number }
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

/**
 * @description get mining dataset stats for iterations
 * @export
 * @param {number} pid
 * @param {number} id
 * @return
 */
export function getMiningStats(pid: number, id: number) {
  return get(id, null, `mining_progress?project_id=${pid}`)
}

/**
 * @description bind task to iteration step
 * @export
 * @param {number} id
 * @param {number} sid
 * @param {number} tid
 * @return
 */
export function bindStep(id: number, sid: number, tid: number) {
  return post(id, { task_id: tid }, `/step/${sid}/bind`)
}

/**
 * @description unbind task from iteration step
 * @export
 * @param {number} id
 * @param {number} sid
 * @return
 */
export function unbindStep(id: number, sid: number) {
  return post(id, null, `/step/${sid}/unbind`)
}

/**
 * @description goto next step
 * @export
 * @param {number} id
 * @param {number} sid
 * @return
 */
export function nextStep(id: number, sid: number) {
  return post(id, null, `/step/${sid}/finish`)
}
