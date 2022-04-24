import task from "../task"
import { put, putResolve, call, select } from "redux-saga/effects"
import { errorCode } from './func'

put.resolve = putResolve

describe("models: task", () => {
  const product = (id) => ({ id })
  const products = (n) => Array.from({ length: n }, (item, index) => product(index + 1))
  errorCode(task, 'getTasks')
  errorCode(task, 'getTask')
  errorCode(task, 'deleteTask')
  errorCode(task, 'updateTask')
  errorCode(task, 'createFusionTask')
  errorCode(task, 'createLabelTask')
  errorCode(task, 'createTrainTask')
  errorCode(task, 'createMiningTask')
  errorCode(task, 'stopTask')

  it("reducers: UPDATE_TASKS, UPDATE_TASK", () => {
    const state = {
      tasks: {},
      task: {},
    }
    const expected = [1, 2, 23, 4, 5, 6, 7, 8, 9]
    const action = {
      payload: { items: expected, total: expected.length },
    }
    const { tasks } = task.reducers.UPDATE_TASKS(state, action)
    const { items, total } = tasks
    expect(items.join(',')).toBe(expected.join(','))
    expect(total).toBe(expected.length)

    const expectedId = 1001
    const daction = {
      payload: { id: expectedId }
    }
    const result = task.reducers.UPDATE_TASK(
      state,
      daction
    )
    expect(result.task.id).toBe(expectedId)
  })

  it("effects: createFusionTask", () => {
    const saga = task.effects.createFusionTask
    const creator = {
      type: "createFusionTask",
      payload: {},
    }
    const expected = "ok"

    const generator = saga(creator, { put, call })
    const start = generator.next()
    generator.next({
      code: 0,
      result: expected,
    })
    generator.next()
    const end = generator.next()

    expect(end.value).toBe(expected)
    expect(end.done).toBe(true)
  })
  it("effects: createTrainTask", () => {
    const saga = task.effects.createTrainTask
    const creator = {
      type: "createTrainTask",
      payload: {},
    }
    const expected = "ok"

    const generator = saga(creator, { put, putResolve, call })
    generator.next()
    generator.next({
      code: 0,
      result: expected,
    })
    generator.next()
    const end = generator.next()

    expect(end.value).toBe(expected)
    expect(end.done).toBe(true)
  })
  it("effects: createMiningTask", () => {
    const saga = task.effects.createMiningTask
    const creator = {
      type: "createMiningTask",
      payload: {},
    }
    const expected = "ok"

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result: expected,
    })
    generator.next()
    const end = generator.next()

    expect(end.value).toBe(expected)
    expect(end.done).toBe(true)
  })
  it("effects: getTasks", () => {
    const saga = task.effects.getTasks
    const creator = {
      type: "getTasks",
      payload: {},
    }
    const expected = {
      items: products(6),
      total: 6,
    }

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result: expected,
    })
    const end = generator.next()

    expect(JSON.stringify(end.value)).toBe(JSON.stringify(expected))
    expect(end.done).toBe(true)
  })
  it("effects: getTask", () => {
    const saga = task.effects.getTask
    const taskId = 620
    const datasetId = 818
    const modelId = 717
    const creator = {
      type: "getTask",
      payload: taskId,
    }
    
    const expected = {
      id: taskId,
      parameters: {
        include_datasets: [datasetId],
        model_id: modelId,
      }
    }
    const datasets = [product(datasetId)]
    const mockModel = product(modelId)

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result: expected,
    })
    generator.next(datasets)
    generator.next(mockModel)
    const end = generator.next()
    const { id, parameters, filterSets, model } = end.value
    expect(id).toBe(taskId)
    expect(parameters.include_datasets[0]).toBe(datasetId)
    expect(filterSets[0].id).toBe(datasetId)
    expect(model.id).toBe(modelId)
    expect(end.done).toBe(true)
  })

  it("effects: createLabelTask", () => {
    const saga = task.effects.createLabelTask
    const creator = {
      type: "createLabelTask",
      payload: {},
    }
    const expected = "ok"

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result: expected,
    })
    
    generator.next()
    const end = generator.next()

    expect(end.value).toBe(expected)
    expect(end.done).toBe(true)
  })
  it("effects: deleteTask", () => {
    const saga = task.effects.deleteTask
    const creator = {
      type: "deleteTask",
      payload: { id: 24 },
    }
    const expected = { id: 24 }

    const generator = saga(creator, { put, call })
    generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    expect(end.value.id).toBe(expected.id)
    expect(end.done).toBe(true)
  })

  it("effects: updateTask", () => {
    const saga = task.effects.updateTask
    const creator = {
      type: "updateTask",
      payload: { id: 234, name: 'iamanewname' },
    }
    const expected = "ok"

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result: expected,
    })
    const end = generator.next()
    expect(end.value).toBe(expected)
    expect(end.done).toBe(true)
  })

  it("effects: stopTask", () => {
    const saga = task.effects.stopTask
    const id = 235
    const creator = {
      type: "stopTask",
      payload: id,
    }
    const expected = { id }

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result: expected,
    })
    generator.next()
    const end = generator.next()

    expect(end.value.id).toBe(id)
    expect(end.done).toBe(true)
  })

  it("effects: stopTask -> success", () => {
    const saga = task.effects.stopTask
    const id = 236
    const creator = {
      type: "stopTask",
      payload: { id },
    }
    const expected = { id }

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result: expected,
    })
    generator.next()
    const end = generator.next()

    expect(end.value.id).toBe(id)
    expect(end.done).toBe(true)
  })
  it("effects: stopTask - no result", () => {
    const saga = task.effects.stopTask
    const id = 236
    const creator = {
      type: "stopTask",
      payload: { id, with_data: true },
    }

    const generator = saga(creator, { put, call })
    generator.next()
    const end = generator.next({
      code: 4002,
      result: null,
    })

    expect(end.value).toBeUndefined()
    expect(end.done).toBe(true)
  })

  it("effects: updateTasks -> normal success", () => {
    const saga = task.effects.updateTasks
    const tasks = {
      items: [
        { id: 34, hash: 'hash1', state: 2, progress: 20 },
        { id: 35, hash: 'hash2', state: 3, progress: 100 },
        { id: 36, hash: 'hash3', state: 2, progress: 96 },
      ], total: 3
    }
    const creator = {
      type: "updateTasks",
      payload: { hash1: { id: 34, state: 2, percent: 0.45 }, hash3: { id: 36, state: 3, percent: 1 } },
    }
    const expected = [
      { id: 34, hash: 'hash1', state: 2, progress: 45 },
      { id: 35, hash: 'hash2', state: 3, progress: 100 },
      { id: 36, hash: 'hash3', state: 3, progress: 100, forceUpdate: true },
    ]

    const generator = saga(creator, { put, call, select })
    generator.next()
    const d = generator.next(tasks)
    const end = generator.next()
    const updated = d.value.payload.action.payload.items

    expect(updated).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it("effects: updateTasks -> empty success", () => {
    const saga = task.effects.updateTasks
    const tasks = {
      items: [
        { id: 34, hash: 'hash1', state: 2, progress: 20 },
        { id: 35, hash: 'hash2', state: 3, progress: 100 },
        { id: 36, hash: 'hash3', state: 2, progress: 96 },
      ], total: 3
    }
    const creator = {
      type: "updateTasks",
    }

    const generator = saga(creator, { put, call, select })
    generator.next()
    const d = generator.next(tasks)
    const end = generator.next()
    const updated = d.value.payload.action.payload

    expect(updated).toEqual(tasks)
    expect(end.done).toBe(true)
  })
  
  it("effects: updateTaskState -> normal success -> progress", () => {
    const saga = task.effects.updateTaskState
    const ts = { id: 34, hash: 'hash1', state: 2, progress: 20 }
    const creator = {
      type: "updateTaskState",
      payload: { hash1: { id: 34, state: 2, percent: 0.45 }, hash3: { id: 36, state: 3, percent: 1 } },
    }
    const expected = { id: 34, hash: 'hash1', state: 2, progress: 45 }

    const generator = saga(creator, { put, call, select })
    generator.next()
    const d = generator.next(ts)
    const end = generator.next()
    const updated = d.value.payload.action.payload

    expect(updated).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it("effects: updateTaskState -> normal success -> progress to done", () => {
    const saga = task.effects.updateTaskState
    const ts = { id: 34, hash: 'hash1', state: 2, progress: 20 }
    const creator = {
      type: "updateTaskState",
      payload: { hash1: { id: 34, state: 3, percent: 1 }, hash3: { id: 36, state: 3, percent: 1 } },
    }
    const expected = { id: 34, hash: 'hash1', state: 3, progress: 100, forceUpdate: true }

    const generator = saga(creator, { put, call, select })
    generator.next()
    const d = generator.next(ts)
    const end = generator.next()
    const updated = d.value.payload.action.payload

    expect(updated).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it("effects: updateTaskState -> empty success", () => {
    const saga = task.effects.updateTaskState
    const ts = { id: 34, hash: 'hash1', state: 2, progress: 20 }
    const creator = {
      type: "updateTaskState",
    }

    const generator = saga(creator, { put, call, select })
    generator.next()
    const d = generator.next(ts)
    const end = generator.next()
    const updated = d.value.payload.action.payload

    expect(updated).toEqual(ts)
    expect(end.done).toBe(true)
  })
})
