import {
  getProjects,
  getProject,
  delProject,
  createProject,
  updateProject,
  addExampleProject,
  checkStatus,
} from "../project"
import { product, products, requestExample } from './func'

describe("service: projects", () => {
  it("getProjects -> success", () => {
    const params = { name: 'testname', offset: 0, limit: 10 }
    const params2 = {}
    const expected = products(15)
    requestExample(getProjects, params, { items: expected, total: expected.length }, 'get')
    requestExample(getProjects, params2, { items: expected, total: expected.length })
  })
  it("getProject -> success", () => {
    const id = 9623
    const expected = {
      id,
      name: '63projectname',
    }
    requestExample(getProject, { id }, expected, 'get')
  })

  it("delProject -> success", () => {
    const id = 9638
    const expected = "ok"
    requestExample(delProject, id, expected)
  })
  it("updateProject -> success", () => {
    const id = 9637
    const project = {
      description: 'memo',
      iteration_target: 10,
      keywords: ['cat', 'dog'],
      name: 'newporjectname',
      training_dataset_count_target: 0,
      type: 0,
    }
    const expected = { id, name }
    requestExample(updateProject, [id, project], expected, 'post')
  })
  it("createProject -> success", () => {
    const project = {
      description: 'memo',
      iteration_target: 10,
      keywords: ['cat', 'dog'],
      name: 'newporjectname',
      training_dataset_count_target: 0,
      type: 0,
    }
    const expected = "ok"
    requestExample(createProject, project, expected, 'post')
  })
  it("checkStatus -> success", () => {
    const pid = 2532432
    const expected = "ok"
    requestExample(checkStatus, pid, expected)
  })
  it("addExampleProject -> success", () => {
    const project = {
      is_example: true,
      description: 'memo',
      iteration_target: 10,
      keywords: ['cat', 'dog'],
      name: 'newporjectname',
      training_dataset_count_target: 0,
      type: 0,
    }
    const expected = "ok"
    requestExample(addExampleProject, project, expected, 'post')
  })
})
