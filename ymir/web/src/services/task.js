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
 * {number} [sampling_count] default: 0
 * }
 * @returns 
 */
export function createFusionTask({
  iteration, project_id, group_id, dataset, include_datasets = [], mining_strategy, include_strategy = 2,
  exclude_result, exclude_datasets = [], include = [], exclude = [], samples,
}) {
  return request.post('/datasets/fusion', {
    project_id, include_datasets, exclude_datasets,
    iteration_context: iteration ? {
      iteration_id: iteration,
      mining_strategy,
      exclude_last_result: exclude_result,
    } : undefined,
    dataset_group_id: group_id,
    main_dataset_id: dataset,
    include_strategy,
    include_labels: include,
    exclude_labels: exclude,
    sampling_count: samples || 0,
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
  projectId, iteration, stage,
  groupId, name, datasetId, keywords,
  labellers, keepAnnotations, doc,
}) {
  return createTask({
    name,
    type: TASKTYPES.LABEL,
    project_id: projectId,
    iteration_id: iteration,
    iteration_stage: stage,
    parameters: {
      dataset_group_id: groupId,
      dataset_id: datasetId,
      keywords,
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
  iteration, stage,
  name, projectId, datasetId, keywords, testset,
  backbone, config, network, trainType, strategy,
  model, image, imageId,
}) {
  return createTask({
    name,
    project_id: projectId,
    iteration_id: iteration,
    iteration_stage: stage,
    type: TASKTYPES.TRAINING,
    docker_image_config: config,
    parameters: {
      strategy,
      dataset_id: datasetId,
      validation_dataset_id: testset,
      keywords,
      backbone,
      network,
      train_type: trainType,
      model_id: model,
      docker_image: image,
      docker_image_id: imageId,
    }
  })
}

export function createMiningTask({
  iteration, stage,
  projectId, datasetId, model, topk, algorithm,
  config, strategy, inference, name, image, imageId,
}) {
  return createTask({
    type: TASKTYPES.MINING,
    project_id: projectId,
    iteration_id: iteration,
    iteration_stage: stage,
    name,
    docker_image_config: config,
    parameters: {
      strategy,
      model_id: model,
      dataset_id: datasetId,
      mining_algorithm: algorithm,
      top_k: topk,
      generate_annotations: inference,
      docker_image: image,
      docker_image_id: imageId,
    }
  })
}

/**
 * create inference task
 * @param {object} task {
 * {string} name
 * {number} projectId
 * {number} datasetId
 * {object} config
 * {number} model
 * {string} image
 * {string} imageId
 * {string} description
 * } 
 * @returns 
 */
export function createInferenceTask({
  name,
  projectId,
  datasetId,
  model = [],
  config,
  image,
  imageId,
  description,
}) {
  const params = model.map(md => ({
    name,
    type: TASKTYPES.INFERENCE,
    project_id: projectId,
    description,
    docker_image_config: config,
    parameters: {
      model_id: md,
      generate_annotations: true,
      dataset_id: datasetId,
      docker_image: image,
      docker_image_id: imageId,
    }
  }))
  return request.post("/tasks/batch", { payloads: params })
}

export function createTask(params) {
  return request.post("/tasks/", params)
}
