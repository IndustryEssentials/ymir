import request from "@/utils/request"
import { TASKTYPES } from "../constants/task"

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

export function createFilterTask({
  name,
  datasets,
  include = [],
  exclude = [],
}) {
  return createTask({
    type: TASKTYPES.FILTER,
    name,
    parameters: {
      name,
      include_datasets: datasets,
      include_classes: include,
      exclude_classes: exclude,
    },
  })
}


export function createLabelTask({
  name,
  datasets,
  label_members,
  keywords,
  doc,
}) {
  return createTask({
    name,
    type: TASKTYPES.LABEL,
    parameters: {
      include_datasets: [datasets],
      labellers: label_members,
      include_classes: keywords,
      extra_url: doc,
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
  // gpu_count,
}) {
  return createTask({
    name,
    type: TASKTYPES.TRAINING,
    config,
    parameters: {
      include_train_datasets: train_sets,
      include_validation_datasets: validation_sets,
      include_classes: keywords,
      backbone,
      hyperparameter,
      network,
      train_type,
      // gpu_count,
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
  name,
  // gpu_count,
}) {
  return createTask({
    type: TASKTYPES.MINING,
    name,
    config,
    parameters: {
      model_id: model,
      include_datasets: datasets,
      exclude_datasets: exclude_sets,
      mining_algorithm: algorithm,
      top_k: topk,
      // gpu_count,
    }
  })
}

export function createTask(params) {
  return request.post("/tasks/", params)
}
