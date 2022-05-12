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
 * }
 * @returns
 */
export function createProject({
  name,
  description,
  targetIteration,
  targetMap,
  targetDataset,
  keywords,
}) {
  return request.post("/projects/", {
    name,
    description,
    training_type: 1,
    iteration_target: targetIteration,
    map_target: targetMap,
    training_dataset_count_target: targetDataset,
    training_keywords: keywords,
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
 * {number} targetIteration
 * {number} targetMap
 * {number} targetDataset
 * {number} strategy
 * {number} chunkSize
 * {string} description
 * {number} trainSetVersion
 * {number} miningSet
 * {number} testSet
 * {number} model
 * }
 * @returns 
 */
export function updateProject(id, {
  name,
  targetIteration,
  keywords,
  targetMap,
  targetDataset,
  strategy,
  chunkSize,
  description,
  trainSetVersion,
  miningSet,
  testSet,
  model,
}) {
  return request({
    method: "patch",
    url: `/projects/${id}`,
    data: {
      name,
      keywords,
      iteration_target: targetIteration,
      map_target: targetMap,
      training_dataset_count_target: targetDataset,
      mining_strategy: strategy,
      chunk_size: chunkSize,
      mining_dataset_id: miningSet,
      testing_dataset_id: testSet,
      description,
      initial_model_id: model,
      initial_training_dataset_id: trainSetVersion,
    },
  })
}

/**
 * get project status, dirty/clean
 * @param {number} pid 
 * @returns 
 */
export function checkStatus(pid) {
  return request.post(`/projects/${pid}/status`)
}
