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
 * stages     {array<number>} main stages for task
 * datasets   {array<number>} main dataset for task
 * }
 * @returns {Promise<Array>}
 */
export function getTasks({
  stages = [],
  datasets = [],
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
  const stageIds = stages.toString() || null
  const datasetIds = datasets.toString() || null
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
      model_stage_ids: stageIds,
      dataset_ids: datasetIds,
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
export function fusion({
  iteration, project_id, group_id, dataset, include_datasets = [], mining_strategy, include_strategy = 2,
  exclude_result, exclude_datasets = [], include = [], exclude = [], samples,
  result_description: description,
}) {
  return request.post('/datasets/fusion', {
    result_description: description,
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
 * create merge task
 * @param {object} param0 
 * {
 * {number} projectId
 * {number} [group]  group id for generated to
 * {string} [name] dataset name for generated
 * {array<number>} [datasets] merge datasets
 * {array<number>} [excludes]
 * {number} [strategy]
 * {number} description 
 * }
 * @returns 
 */
export function merge({
  projectId, group, name,
  datasets = [], strategy = 2,
  excludes = [],
  description,
}) {
  return request.post('/datasets/merge', {
    project_id: projectId,
    include_datasets: datasets,
    exclude_datasets: excludes,
    dest_group_name: name,
    dest_group_id: group,
    merge_strategy: strategy,
    description,
  })
}
/**
 * create filter task
 * @param {object} param0 
 * {
 * {number} projectId
 * {number} dataset
 * {array<string>} [includes]
 * {array<string>} [excludes]
 * {number} [samples]
 * {number} [description]
 * }
 * @returns 
 */
export function filter({
  projectId, dataset,
  includes, excludes, samples,
  description,
}) {
  return request.post('/datasets/filter', {
    project_id: projectId,
    dataset_id: dataset,
    include_keywords: includes,
    exclude_keywords: excludes,
    sampling_count: samples,
    description,
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
export function label({
  projectId, iteration, stage,
  groupId, name, datasetId, keywords,
  labellers, keepAnnotations, doc, description,
}) {
  return createTask({
    name,
    result_description: description,
    type: TASKTYPES.LABEL,
    project_id: projectId,
    iteration_id: iteration,
    iteration_stage: stage,
    parameters: {
      dataset_group_id: groupId,
      dataset_id: datasetId,
      keywords,
      labellers: ['hide@label.com'],
      extra_url: doc,
      annotation_type: keepAnnotations,
    },
  })
}

/**
 * create training task
 * @param {object} task {
 * {string} name
 * {number} projectId
 * {number} datasetId
 * {number} stage
 * {number} testset
 * {string} backbone
 * {object} config
 * {string} network
 * {number} trainType
 * {number} strategy
 * {array[number, number]} modelStage
 * {string} image
 * } 
 * @returns 
 */
export function train({
  iteration, stage, openpai, description,
  name, projectId, datasetId, keywords, testset,
  backbone, config, network, trainType, strategy,
  modelStage = [], image, imageId, preprocess,
}) {
  const model = modelStage[0]
  const stageId = modelStage[1]
  return createTask({
    name,
    project_id: projectId,
    result_description: description,
    iteration_id: iteration,
    iteration_stage: stage,
    type: TASKTYPES.TRAINING,
    docker_image_config: { ...config, openpai_enable: openpai, },
    preprocess,
    parameters: {
      strategy,
      dataset_id: datasetId,
      validation_dataset_id: testset,
      keywords,
      backbone,
      network,
      train_type: trainType,
      model_id: model,
      model_stage_id: stageId,
      docker_image: image,
      docker_image_id: imageId,
    }
  })
}

export function mine({
  iteration, stage, openpai, description,
  projectId, datasetId, modelStage = [], topk, algorithm,
  config, strategy, inference, name, image, imageId,
}) {
  const model = modelStage[0]
  const stageId = modelStage[1]
  return createTask({
    type: TASKTYPES.MINING,
    project_id: projectId,
    result_description: description,
    iteration_id: iteration,
    iteration_stage: stage,
    name,
    docker_image_config: { ...config, openpai_enable: openpai, },
    parameters: {
      strategy,
      model_id: model,
      model_stage_id: stageId,
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
 * {array<number>} datasets
 * {object} config
 * {array<array<model, stage>>} stages
 * {string} image
 * {string} imageId
 * {string} description
 * } 
 * @returns 
 */
export function infer({
  name,
  projectId,
  datasets,
  stages = [],
  config,
  image,
  imageId,
  openpai,
  description,
}) {
  const maps = datasets.map(dataset => stages.map(([model, stage]) => ({ dataset, model, stage }))).flat()
  const params = maps.map(({ model, stage, dataset }) => ({
    name,
    type: TASKTYPES.INFERENCE,
    project_id: projectId,
    result_description: description,
    docker_image_config: { ...config, openpai_enable: openpai, },
    parameters: {
      model_id: model,
      model_stage_id: stage,
      generate_annotations: true,
      dataset_id: dataset,
      docker_image: image,
      docker_image_id: imageId,
    }
  }))
  return request.post("/tasks/batch", { payloads: params })
}

export function createTask(params) {
  return request.post("/tasks/", params)
}
