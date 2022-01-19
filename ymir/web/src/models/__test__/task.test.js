import task from "../task"
import { put, putResolve, call } from "redux-saga/effects"

put.resolve = putResolve

describe("models: task", () => {
  const product = (id) => ({ id })
  const products = (n) => Array.from({ length: n }, (item, index) => product(index + 1))

  it("reducers: UPDATE_TASKS, UPDATE_TASK", () => {
    const state = {
      datasets: {},
      dataset: {},
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

  it("effects: createFilterTask", () => {
    const saga = task.effects.createFilterTask
    const creator = {
      type: "createFilterTask",
      payload: {},
    }
    const expected = "ok"

    const generator = saga(creator, { put, call })
    const start = generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

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
    const end = generator.next({
      code: 0,
      result: expected,
    })

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
    const end = generator.next({
      code: 0,
      result: expected,
    })

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
    const end = generator.next({
      code: 0,
      result: expected,
    })

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
    generator.next({
      code: 0,
      result: expected,
    })
    const end = generator.next()

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
    const end = generator.next({
      code: 0,
      result: expected,
    })

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
    const end = generator.next({
      code: 0,
      result: expected,
    })

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
})
