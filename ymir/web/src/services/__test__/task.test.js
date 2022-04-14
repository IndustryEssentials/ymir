import {
  getTasks,
  getTask,
  deleteTask,
  updateTask,
  createFusionTask,
  createLabelTask,
  createTrainTask,
  createMiningTask,
  createTask,
  stopTask,
} from "../task"
import { product, products, requestExample } from './func'


describe("service: tasks", () => {
  it("getTasks -> success", () => {
    const params = { name: 'testname', type: 1, state: 1, start_time: 123942134, end_time: 134123434 }
    const len = 12
    const expected = { items: product(len), total: len }
    requestExample(getTasks, params, expected, 'get')
  })
  it("getTask -> success", () => {
    const id = 613
    const expected = {
      id,
      name: '60taskname',
    }
    requestExample(getTask, id, expected, 'get')
  })

  it("createFusionTask -> success, no include classes", () => {
    const params = {
      project_id: 2436,
      dataset_group_id: 2345,
      main_dataset_id: 435,
    }
    const expected = { id: 612 }
    requestExample(createFusionTask, params, expected, 'post')
  })
  it("createFusionTask -> success, no exclude classes", () => {
    const params = {
      project_id: 2436,
      dataset_group_id: 2340,
      main_dataset_id: 432,
      include_datasets: [454, 457],
    }
    const expected = { id: 612 }
    requestExample(createFusionTask, params, expected, 'post')
  })
  it("createFusionTask -> success, all params", () => {
    const params = {
      project_id: 2436,
      dataset_group_id: 2340,
      main_dataset_id: 432,
      include_datasets: [454, 457],
      include_strategy: [1, 2, 3],
      exclude_datasets: [4,5],
      include_labels: ['person'],
      exclude_labels: ['cat', 'dog', 'tree'],
      sampling_count: 1000,
    }
    const expected = { id: 612 }
    requestExample(createFusionTask, params, expected, 'post')
  })

  it("createTrainTask -> success", () => {
    const params = {
      name: 'taskname',
      train_sets: [1, 3, 4],
      validation_sets: [5],
      backbone: 'darknet',
      hyperparameter: 'epco v10',
      network: 'YOLO v4',
      keywords: ['cat', 'dog'],
      train_type: 1,
    }
    const expected = { id: 611 }
    requestExample(createTrainTask, params, expected, 'post')
  })
  it("createMiningTask -> success", () => {
    const params = {
      model: 'modelhash',
      topk: 1000,
      datasets: [1, 2],
      exclude_sets: [],
      algorithm: 'LYDD',
      name: 'taskname',
    }
    const expected = { id: 610 }
    requestExample(createMiningTask, params, expected, 'post')
  })
  it("createLabelTask -> success", () => {
    const params = {
      name: 'taskname',
      datasets: [23, 34],
      label_members: ['a@test.com', 'b@test.com'],
      keywords: ['cat', 'dog'],
      doc: 'http://test.com/test.pdf'
    }
    const expected = { id: 609 }
    requestExample(createLabelTask, params, expected, 'post')
  })
  it("deleteTask -> success", () => {
    const id = 608
    const expected = "ok"
    requestExample(deleteTask, id, expected)
  })
  it("stopTask -> success -> throw result", () => {
    const id = 607
    const expected = { id }
    requestExample(stopTask, id, expected, 'post')
  })
  it("stopTask -> success -> with result", () => {
    const id = 607
    const fetch_result = true
    const expected = { id }
    requestExample(stopTask, [id, fetch_result], expected, 'post')
  })
  it("updateTask -> success", () => {
    const id = 607
    const name = 'newnameoftask'
    const expected = { id, name }
    requestExample(updateTask, [id, name], expected)
  })
  it("createTask -> success", () => {
    const params = {
      name: 'newtask',
    }
    const expected = "ok"
    requestExample(createTask, params, expected, 'post')
  })
})
