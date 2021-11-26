import keyword from "../keyword"
import { put, call, select } from "redux-saga/effects"

describe("models: keyword", () => {
  it("effects: getKeywords", () => {
    const saga = keyword.effects.getKeywords
    const creator = {
      type: "getKeywords",
      payload: {},
    }
    const keywords = [1, 2, 3, 4]
    const expected = { code: 0, result: keywords }

    const generator = saga(creator, { put, call, select })
    const start = generator.next()
    const response = generator.next(expected)
    const end = generator.next()

    expect(expected.result).toEqual(end.value)
    expect(end.done).toBe(true)
  })
})