import iteration from "../iteration"
import { put, putResolve, call, select } from "redux-saga/effects"
import {
  product,
  products,
  errorCode,
  normalReducer,
  generatorCreator,
} from "./func"
import { Stages, transferIteration } from "@/constants/iteration"

put.resolve = putResolve

function equalObject(obj1, obj2) {
  expect(JSON.stringify(obj1)).toBe(JSON.stringify(obj2))
}

describe("models: iteration", () => {
  const createGenerator = generatorCreator(iteration)
  normalReducer(
    iteration,
    "UPDATE_ITERATIONS",
    { id: 13424, iterations: product(34) },
    { 13424: product(34) },
    "iterations",
    {}
  )
  normalReducer(
    iteration,
    "UPDATE_ITERATION",
    product(100434),
    { 100434: product(100434) },
    "iteration",
    {}
  )

  errorCode(iteration, "getIterations")
  errorCode(iteration, "createIteration")
  errorCode(iteration, "updateIteration")

  it("effects: getIterations -> success", () => {
    const iterations = products(5)
    const expected = iterations.map((i) => transferIteration(i))

    const generator = createGenerator("getIterations", {})
    generator.next()
    generator.next({
      code: 0,
      result: iterations,
    })
    generator.next()
    const end = generator.next()

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })

  it("effects: getIteration", () => {
    const id = 10012
    const pid = 62314
    const result = { id, project_id: pid, name: "iteration001" }
    const expected = transferIteration(result)

    const generator = createGenerator("getIteration", { pid, id })
    generator.next()
    generator.next()
    generator.next(expected)
    const end = generator.next()

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it("effects: getStageResult", () => {
    const stage = 1
    const pid = 62314
    const result = { id: 254, project_id: pid, name: "iteration002" }
    const expected = result

    const generator = createGenerator("getStageResult", { id: pid, stage })
    generator.next()
    const end = generator.next(result)

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it("effects: getStageResult -> get model", () => {
    const stage = Stages.training
    const pid = 62314
    const result = product(2345)
    const expected = result

    const generator = createGenerator("getStageResult", {
      id: pid,
      stage,
      force: true,
    })
    generator.next()
    const end = generator.next(result)

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it("effects: createIteration", () => {
    const id = 10015
    const result = { id, name: "new_iteration_name" }
    const expected = transferIteration(result)

    const generator = createGenerator("createIteration", {
      name: "new_iteration_name",
      type: 1,
    })
    generator.next()
    generator.next({
      code: 0,
      result,
    })
    generator.next()
    generator.next([])
    const end = generator.next()

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it("effects: updateIteration", () => {
    const origin = { id: 10011, name: "new_iteration_name" }

    const expected = transferIteration(origin)
    const generator = createGenerator("updateIteration", origin)

    generator.next()
    generator.next({
      code: 0,
      result: expected,
    })
    generator.next()
    generator.next([])
    const end = generator.next()

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
})
