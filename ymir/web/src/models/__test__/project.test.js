import project from "../project"
import { put, call, select } from "redux-saga/effects"
import { errorCode } from "./func"
import { format } from "@/utils/date"
import { transferProject } from '@/constants/project'

function equalObject(obj1, obj2) {
  expect(JSON.stringify(obj1)).toBe(JSON.stringify(obj2))
}

describe("models: project", () => {
  const product = (id) => ({ id })
  const products = (n) =>
    Array.from({ length: n }, (item, index) => product(index + 1))
  it("reducers: UPDATE_LIST", () => {
    const state = {
      list: { items: [], total: 0 },
    }
    const expected = { items: [1, 2, 3, 4], total: 4 }
    const action = {
      payload: expected,
    }
    const result = project.reducers.UPDATE_LIST(state, action)
    expect(result.list).toEqual(expected)
  })
  it("reducers: UPDATE_PROJECTS", () => {
    const state = {
      projects: {},
    }
    const expected = { id: 10013 }
    const action = {
      payload: expected,
    }
    const result = project.reducers.UPDATE_PROJECTS(state, action)
    expect(result.projects[expected.id]).toEqual(expected)
  })

  errorCode(project, "getProjects")
  // errorCode(project, "getProject")
  errorCode(project, "delProject")
  errorCode(project, "createProject")
  errorCode(project, "addExampleProject")
  errorCode(project, "updateProject")
  errorCode(project, "checkStatus")

  it("effects: getProjects -> success", () => {
    const saga = project.effects.getProjects
    const creator = {
      type: "getProjects",
      payload: {},
    }
    const projects = products(9)
    const expected = projects.map(item => transferProject(item))
    const result = { items: projects, total: projects.length }

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result,
    })
    const end = generator.next()

    expect(end.value).toEqual({
      items: expected,
      total: projects.length,
    })
    expect(end.done).toBe(true)
  })

  it("effects: getProject", () => {
    const saga = project.effects.getProject
    const id = 10012
    const creator = {
      type: "getProject",
      payload: { id },
    }
    const expected = { id, name: "project001" }

    const generator = saga(creator, { put, call, select })
    generator.next()
    generator.next({})
    generator.next({
      code: 0,
      result: expected,
    })
    const end = generator.next()

    expect(end.value).toEqual(transferProject(expected))
    expect(end.done).toBe(true)
  })
  it("effects: delProject", () => {
    const saga = project.effects.delProject
    const id = 10014
    const creator = {
      type: "delProject",
      payload: id,
    }
    const expected = { id, name: "del_project_name" }

    const generator = saga(creator, { put, call })
    generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    equalObject(expected, end.value)
    expect(end.done).toBe(true)
  })
  it("effects: createProject", () => {
    const saga = project.effects.createProject
    const id = 10015
    const expected = { id, name: "new_project_name" }
    const creator = {
      type: "createProject",
      payload: { name: "new_project_name", type: 1 },
    }

    const generator = saga(creator, { put, call })
    generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    equalObject(expected, end.value)
    expect(end.done).toBe(true)
  })
  it("effects: addExampleProject", () => {
    const saga = project.effects.addExampleProject
    const id = 10019
    const expected = { id, name: "example_project_name" }
    const creator = {
      type: "addExampleProject",
      payload: { name: "example_project_name", type: 1 },
    }

    const generator = saga(creator, { put, call })
    generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    equalObject(expected, end.value)
    expect(end.done).toBe(true)
  })
  it("effects: updateProject", () => {
    const saga = project.effects.updateProject
    const creator = {
      type: "updateProject",
      payload: { id: 10011, name: "new_project_name" },
    }
    const expected = { id: 10011, name: "new_project_name" }

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result: expected,
    })
    const end = generator.next()

    equalObject(expected, end.value)
    expect(end.done).toBe(true)
  })
  it("effects: checkStatus", () => {
    const saga = project.effects.checkStatus
    const pid = 2346349
    const expected = { is_dirty: true }
    const creator = {
      type: "checkStatus",
      payload: pid,
    }

    const generator = saga(creator, { put, call })
    generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
})
