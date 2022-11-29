import request from "@/utils/request"

/** project service */
/**
 *
 * @param {array[number]} id
 * @returns
 */
export function getProject(id) {
  return request.get(`projects/${id}`)
}

/**
 * @param {*} params
 * { name, offset = 0, limit = 10 }
 * @returns
 */
export function getProjects({ name, offset = 0, limit = 0 }) {
  return request.get("projects/", { params: { name, offset, limit } })
}

/**
 * delete project
 * @param {number} id
 * @returns
 */
export function delProject(id) {
  return request({
    method: "delete",
    url: `/projects/${id}`,
  })
}

/**
 * create a project
 * @param {object} project
 * {
 *   {string}  name
 *   {string}  [description]
 *   {number}  [target_iteration]
 *   {number}  [target_map]
 *   {number}  [target_dataset]
 *   {array<string>}  keywords
 *   {boolean} enableIteration
 * }
 * @returns
 */
export function createProject({
  name,
  description,
  keywords,
  strategy = 1,
  enableIteration,
}) {
  return request.post("/projects/", {
    name,
    description,
    training_type: 1,
    training_keywords: keywords,
    mining_strategy: strategy,
    enable_iteration: enableIteration
  })
}

/**
 * create an example project
 * @returns
 */
export function addExampleProject() {
  return request.post("/projects/samples")
}

/**
 * update project
 * @param {number} id 
 * @param {object} params 
 * {
 * {string} name
 * {number} strategy
 * {number} chunkSize
 * {string} description
 * {number} trainSetVersion
 * {number} miningSet
 * {number} testSet
 * {number} [modelStage]
 * {boolean} enableIteration
 * {array<number>} [testingSets]
 * }
 * @returns 
 */
export function updateProject(id, {
  name,
  keywords,
  strategy,
  chunkSize,
  description,
  candidateTrainSet,
  trainSetVersion,
  miningSet,
  testSet,
  modelStage = [],
  enableIteration,
  testingSets,
}) {
  const [model, stage] = modelStage
  return request({
    method: "patch",
    url: `/projects/${id}`,
    data: {
      name,
      training_keywords: keywords,
      mining_strategy: strategy,
      chunk_size: chunkSize,
      mining_dataset_id: miningSet,
      validation_dataset_id: testSet,
      description,
      initial_model_id: model,
      initial_model_stage_id: stage,
      initial_training_dataset_id: trainSetVersion,
      candidate_training_dataset_id: candidateTrainSet,
      enable_iteration: enableIteration,
      testing_dataset_ids: testingSets ? testingSets?.toString() : undefined,
    },
  })
}

/**
 * get project status, dirty/clean
 * @param {number} pid 
 * @returns 
 */
export function checkStatus(pid) {
  return request.get(`/projects/${pid}/status`)
}
