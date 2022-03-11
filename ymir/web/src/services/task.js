import request from "@/utils/request"
import { TASKTYPES } from "@/constants/task"

/**
 * get (or filter) task list
 * @param {object} 
 * {
 * name       {string}      task name (for filter)
 * type       {number}      task type (for filter)
 * state      {number}      task state (for filter)
 * start_time {timestamp}   start time of create time (for filter)
 * end_time   {timestamp}   end time of create time (for filter)
 * offset     {number}      start offset
 * limit      {number}      items of fetch, as page size
 * }
 * @returns {Promise<Array>}
 */
export function getTasks({
  name,
  type,
  state,
  start_time,
  end_time,
  offset = 0,
  limit = 20,
  is_desc,
  order_by,
}) {
  return request.get("/tasks/", {
    params: {
      name,
      type,
      state,
      start_time,
      end_time,
      offset,
      limit,
      is_desc,
      order_by,
    },
  })
}

/**
 * get single task
 * @param {number} id  task id
 * @returns 
 */
export function getTask(id) {
  return request.get(`/tasks/${id}`)
}

/**
 * delete task
 * @param {number} id 
 * @returns 
 */
export function deleteTask(id) {
  return request({
    method: 'DELETE',
    url: `/tasks/${id}`
  })
}

/**
 * stop task( and get label data for label task)
 * @param {number} id 
 * @param {boolean} [fetch_result] fetch result or not
 * @returns 
 */
export function stopTask(id, fetch_result = false) {
  return request.post(`/tasks/${id}/terminate`, { fetch_result })
}

/**
 * update task, only support task name now
 * @param {number} id 
 * @param {string} name 
 * @returns 
 */
export function updateTask(id, name) {
  return request({
    method: 'PATCH',
    url: `/tasks/${id}`,
    data: { name }
  })
}

/**
 * create fusion task
 * @param {object} param0 
 * {
 * {number} project_id
 * {number} dataset_group_id
 * {number} main_dataset_id 
 * {array<number>} [include_datasets]
 * {number} [include_strategy]
 * {array<number>} [exclude_datasets]
 * {array<string>} [include_labels]
 * {array<string>} [exclude_labels]
 * {number} [sampling_count]
 * }
 * @returns 
 */
export function createFusionTask({
  project_id, group_id, dataset, include_datasets = [], strategy = 2,
  exclude_datasets = [], include = [], exclude = [], samples,
}) {
  return request.post('/datasets/fusion', {
    project_id, include_datasets, exclude_datasets,
    dataset_group_id: group_id,
    main_dataset_id: dataset,
    include_strategy: strategy,
    include_labels: include,
    exclude_labels: exclude,
    sampling_count: samples,
  })
}

/**
 * create label task
 * @param {object} task {
 * {number} projectId
 * {string} name
 * {number} datasetId
 * {array<string>} labellers
 * {boolean} keepAnnotations
 * {string} doc
 * } 
 * @returns 
 */
export function createLabelTask({
  projectId,
  name,
  datasetId,
  labellers,
  keepAnnotations,
  doc,
}) {
  return createTask({
    name,
    type: TASKTYPES.LABEL,
    project_id: projectId,
    parameters: {
      dataset_id: datasetId,
      labellers,
      extra_url: doc,
      keep_annotations: keepAnnotations,
    },
  })
}

/**
 * create training task
 * @param {object} task {
 * {string} name
 * {number} projectId
 * {number} datasetId
 * {number} testset
 * {string} backbone
 * {object} config
 * {string} network
 * {number} trainType
 * {number} strategy
 * {number} model
 * {string} image
 * } 
 * @returns 
 */
export function createTrainTask({
  name,
  projectId,
  datasetId,
  testset,
  backbone,
  config,
  network,
  trainType,
  strategy,
  model,
  image,
}) {
  return createTask({
    name,
    project_id: projectId,
    type: TASKTYPES.TRAINING,
    config,
    parameters: {
      strategy,
      dataset_id: datasetId,
      validation_dataset_id: testset,
      backbone,
      network,
      train_type: trainType,
      model_id: model,
      docker_image: image,
    }
  })
}

export function createMiningTask({
  model,
  topk,
  datasets,
  exclude_sets,
  algorithm,
  config,
  strategy,
  inference,
  name,
  docker_image,
  docker_image_id,
}) {
  return createTask({
    type: TASKTYPES.MINING,
    name,
    config,
    parameters: {
      strategy,
      model_id: model,
      include_datasets: datasets,
      exclude_datasets: exclude_sets,
      mining_algorithm: algorithm,
      top_k: topk,
      generate_annotations: inference,
      docker_image,
      docker_image_id,
    }
  })
}

export function createTask(params) {
  return request.post("/tasks/", params)
}
