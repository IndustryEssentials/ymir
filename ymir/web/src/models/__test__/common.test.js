import common from "../common"
import { put, call, select } from "redux-saga/effects"

function equalArray (arr1, arr2) {
  expect(arr1.join(',')).toBe(arr2.join(','))
}

function equalObject(obj1, obj2) {
  expect(JSON.stringify(obj1)).toBe(JSON.stringify(obj2))
}

describe("models: common", () => {

  it("effects: getStats", () => {
    const saga = common.effects.getStats
    const creator = {
      type: "getStats",
      payload: {},
    }
    const expected = {
      "code": 0,
      "message": "success",
      "result": {
        "dataset": [
          "string"
        ],
        "model": [
          "string"
        ],
        "task": [
          "string"
        ],
        "task_timestamps": [
          "string"
        ]
      }
    }

    const generator = saga(creator, { put, call })
    const start = generator.next()
    const end = generator.next(expected)

    equalObject(expected.result, end.value)
    expect(end.done).toBe(true)

    const error = saga(creator, { put, call})
    error.next()
    const errorEnd = error.next({
      code: 13001,
      result: null,
    })

    expect(errorEnd.value).toBeUndefined()
    expect(errorEnd.done).toBe(true)
  })

  it("effects: getSysInfo", () => {
    const saga = common.effects.getSysInfo
    const creator = {
      type: "getSysInfo",
      payload: { },
    }
    const expected = {
      gpu_count: 8,
    }

    const generator = saga(creator, { call })
    const start = generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    expect(end.done).toBe(true)
    expect(end.value.gpu_count).toBe(expected.gpu_count)

    const errGen = saga(creator, { call })
    errGen.next()
    const errEnd = errGen.next({
      code: 110104,
      result: expect,
    })
    expect(errEnd.done).toBe(true)
    expect(errEnd.value).toBe(undefined)
  })
})
