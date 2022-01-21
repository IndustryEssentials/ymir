import keyword from "../keyword"
import { put, call, select } from "redux-saga/effects"
import { errorCode } from './func'

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
    const response = generator.next(expected)
    const end = generator.next()

    expect(expected.result).toEqual(end.value)
    expect(end.done).toBe(true)
  })
  it("effects: updateKeywords", () => {
    const saga = keyword.effects.updateKeywords
    const kw = { name: 'cat', aliases: ['kitty', 'hunney'] }
    const creator = {
      type: "updateKeywords",
      payload: { keywords: [kw], dry_run: false},
    }
    const keywords = [kw]
    const response = { code: 0, result: keywords }

    const generator = saga(creator, { put, call })
    const start = generator.next()
    const end = generator.next(response)

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
    const start = generator.next()
    const end = generator.next(response)

    expect(response.result).toEqual(end.value)
    expect(end.done).toBe(true)
  })
  it("effects: getRecommendKeywords", () => {
    const saga = keyword.effects.getRecommendKeywords
    const kw = [['cat', 12], ['dog', 6], ['person', 3]]
    const expected = kw.map(item => item[0])
    const creator = {
      type: "getRecommendKeywords",
      payload: kw,
    }
    const response = { code: 0, result: kw }

    const generator = saga(creator, { put, call, select })
    generator.next()
    const end = generator.next(response)

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it('test reducers: UPDATE_KEYWORDS, UPDATE_KEYWORD', () => {
    const state = {
      keywords: {
        items: [],
        total: 0,
      },
      keyword: {},
    }

    const expected = products(10)
    const action = {
      payload: { items: expected, total: expected.length },
    }
    const { keywords } = keyword.reducers.UPDATE_KEYWORDS(state, action)
    const { items, total } = keywords
    expect(items.join(',')).toBe(expected.join(','))
    expect(total).toBe(expected.length)

    const expected2 = 'keywordname677'
    const daction = {
      payload: { name: expected2 }
    }
    const result = keyword.reducers.UPDATE_KEYWORD(state, daction)
    expect(result.keyword.name).toBe(expected2)
  })
})