import keyword from "../keyword"
import { put, call, select, putResolve } from "redux-saga/effects"
import { errorCode } from './func'

put.resolve = putResolve

describe("models: keyword", () => {
  const product = (id) => ({ id })
  const products = (n) => Array.from({ length: n }, (item, index) => product(index + 1))
  errorCode(keyword, 'getKeywords')
  errorCode(keyword, 'updateKeywords')
  errorCode(keyword, 'updateKeyword')
  errorCode(keyword, 'getRecommendKeywords')
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
     const end = generator.next(expected)

    expect(expected.result).toEqual(end.value)
    expect(end.done).toBe(true)
  })
  it("effects: updateKeywords", () => {
    const saga = keyword.effects.updateKeywords
    const kw = { name: 'cat', aliases: ['kitty', 'hunney'] }
    const creator = {
      type: "updateKeywords",
      payload: { keywords: [kw], dry_run: false },
    }
    const keywords = [kw]
    const response = { code: 0, result: keywords }

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next(response)
    const end = generator.next()

    expect(end.value).toEqual(response.result)
    expect(end.done).toBe(true)
  })
  it("effects: updateKeyword", () => {
    const saga = keyword.effects.updateKeyword
    const kw = { name: 'cat', aliases: ['kitty', 'hunney'] }
    const creator = {
      type: "updateKeyword",
      payload: kw,
    }
    const response = { code: 0, result: kw }

    const generator = saga(creator, { put, call, select })
    generator.next()
    generator.next(response)
    const end = generator.next()

    expect(response.result).toEqual(end.value)
    expect(end.done).toBe(true)
  })
  it("effects: getRecommendKeywords", () => {
    const saga = keyword.effects.getRecommendKeywords
    const result = [{ legend: 'cat', count: 12 }, { legend: 'dog', count: 6 }, { legend: 'person', count: 3 }]
    const expected = result.map(item => item.legend)
    const creator = {
      type: "getRecommendKeywords",
      payload: { datasets: [34, 4], limit: 5 },
    }
    const response = { code: 0, result }

    const generator = saga(creator, { put, call, select })
    generator.next()
    const end = generator.next(response)

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it('test reducers: UPDATE_KEYWORDS, UPDATE_KEYWORD', () => {
    const state = {
      allKeywords: [],
      reload: true,
    }

    const expected = ['person', 'cat', 'dog'].map(item => ({ name: item, aliases: [] }))
    const action = {
      payload: expected,
    }
    const { allKeywords } = keyword.reducers.UpdateAllKeywords(state, action)
    expect(allKeywords).toEqual(expected)

    const daction = {
      payload: false
    }
    const { reload } = keyword.reducers.UpdateReload(state, daction)
    expect(reload).toBe(false)
  })
})