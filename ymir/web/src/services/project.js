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
 * update project
 * @param {number} id 
 * @param {object} params 
 * {
 * {string} name
 * {number} iteration_target
 * {number} map_target
 * {number} training_dataset_count_target
 * {number} mining_strategy
 * {number} chunk_size
 * {number} training_dataset_group_id
 * {number} mining_dataset_id
 * {number} testing_dataset_id
 * {string} description
 * {number} initial_model_id
 * }
 * @returns 
 */
export function updateProject(id, {
  name,
  targetIteration,
  targetMap,
  targetDataset,
  strategy,
  chunkSize,
  description,
  miningSet,
  testSet,
  model,
}) {
  return request({
    method: "patch",
    url: `/projects/${id}`,
    data: {
      name,
      iteration_target: targetIteration,
      map_target: targetMap,
      training_dataset_count_target: targetDataset,
      mining_strategy: strategy,
      chunk_size: chunkSize,
      training_dataset_group_id: 0,
      mining_dataset_id: miningSet,
      testing_dataset_id: testSet,
      description,
      initial_model_id: model,
    },
  })
}
