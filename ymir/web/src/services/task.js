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
  project_id, dataset_group_id, main_dataset_id, include_datasets = [], include_strategy = [],
  exclude_datasets = [], include_labels = [], exclude_labels = [], sampling_count,
}) {
  return request.post('​/datasets​/dataset_fusion', {
    project_id, dataset_group_id, main_dataset_id, include_datasets, include_strategy, exclude_datasets, include_labels, exclude_labels, sampling_count,
  })
}


export function createLabelTask({
  name,
  datasets,
  label_members,
  keywords,
  with_labels,
  keep_annotations,
  doc,
}) {
  return createTask({
    name,
    type: TASKTYPES.LABEL,
    parameters: {
      with_labels,
      include_datasets: [datasets],
      labellers: label_members,
      include_classes: keywords,
      extra_url: doc,
      keep_annotations,
      with_labels,
    },
  })
}

export function createTrainTask({
  name,
  train_sets,
  validation_sets,
  backbone,
  hyperparameter,
  config,
  network,
  keywords,
  train_type,
  strategy,
  model,
  docker_image,
  docker_image_id,
}) {
  return createTask({
    name,
    type: TASKTYPES.TRAINING,
    config,
    parameters: {
      strategy,
      include_train_datasets: train_sets,
      include_validation_datasets: validation_sets,
      include_classes: keywords,
      backbone,
      hyperparameter,
      network,
      train_type,
      model_id: model,
      docker_image,
      docker_image_id,
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
