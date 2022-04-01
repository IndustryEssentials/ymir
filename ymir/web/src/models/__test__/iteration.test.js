import iteration from "../iteration"
import { put, call, select } from "redux-saga/effects"
import { errorCode } from "./func"
import { transferIteration } from '@/constants/project'

function equalObject(obj1, obj2) {
  expect(JSON.stringify(obj1)).toBe(JSON.stringify(obj2))
}

describe("models: iteration", () => {
  const product = (id) => ({ id })
  const products = (n) =>
    Array.from({ length: n }, (item, index) => product(index + 1))
  it("reducers: UPDATE_ITERATIONS", () => {
    const state = {
      iterations: {},
    }
    const expected = { id: 13424, iterations: product(34) }
    const action = {
      payload: expected,
    }
    const result = iteration.reducers.UPDATE_ITERATIONS(state, action)
    expect(result.iterations[expected.id]).toEqual(expected.iterations)
  })
  it("reducers: UPDATE_ITERATION", () => {
    const state = {
      iteration: {},
    }
    const expected = product(100434)
    const action = {
      payload: expected,
    }
    const result = iteration.reducers.UPDATE_ITERATION(state, action)
    expect(result.iteration).toEqual(expected)
  })

  errorCode(iteration, "getIterations")
  errorCode(iteration, "getIteration")
  errorCode(iteration, "createIteration")
  errorCode(iteration, "updateIteration")

  it("effects: getIterations -> success", () => {
    const saga = iteration.effects.getIterations
    const creator = {
      type: "getIterations",
      payload: {},
    }
    const iterations = products(5)
    const expected = iterations.map(i => transferIteration(i))

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result: iterations,
    })
    const end = generator.next()

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })

  it("effects: getIteration", () => {
    const saga = iteration.effects.getIteration
    const id = 10012
    const creator = {
      type: "getIteration",
      payload: id,
    }
    const result = { id, name: "iteration001" }
    const expected = transferIteration(result)

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result,
    })
    const end = generator.next()

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it("effects: createIteration", () => {
    const saga = iteration.effects.createIteration
    const id = 10015
    const expected = { id, name: "new_iteration_name" }
    const creator = {
      type: "createIteration",
      payload: { name: "new_iteration_name", type: 1 },
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
  it("effects: updateIteration", () => {
    const saga = iteration.effects.updateIteration
    const creator = {
      type: "updateIteration",
      payload: { id: 10011, name: "new_iteration_name" },
    }
    const expected = { id: 10011, name: "new_iteration_name","round":0,"currentStage":0,"prevIteration":0 }

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
