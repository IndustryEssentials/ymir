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
  })
  it("effects: getHistory", () => {
    const saga = common.effects.getHistory
    const creator = {
      type: "getLabels",
      payload: {},
    }
    const expected = {
      "code": 0,
      "message": "success",
      "result": {
        "nodes": [
          {
            "id": '1001',
            "name": "history_dataset",
            "hash": "a2347sdfkj27adflkw34uasdfj",
            "type": 1,
            "proprieties": {}
          },
          {
            "id": '1002',
            "name": "history_model",
            "hash": "a2347sdfkj27adflkw34uasdfj",
            "type": 1,
            "proprieties": {}
          }
        ],
        "edges": [
          {
            "source": "1001",
            "target": "1002",
            "task": {
              "id": 10001,
              "name": "task1",
              "hash": "quasdfjadlfjasdf",
              "type": 2,
              "proprieties": {}
            }
          }
        ]
      }
    }

    const generator = saga(creator, { put, call })
    const start = generator.next()
    const end = generator.next(expected)

    equalObject(expected.result, end.value)
    expect(end.done).toBe(true)
  })

  it("effects: getRuntimes", () => {
    const saga = common.effects.getRuntimes
    const creator = {
      type: "getRuntimes",
      payload: { type: 1 },
    }
    const expected = {
      a: 1,
      b: 2,
      c: 3,
    }

    const generator = saga(creator, { put, call })
    const start = generator.next()
    const end = generator.next({
      code: 0,
      result: [expected],
    })

    expect(end.done).toBe(true)
    expect(end.value).toBe(expected)
  })
})
