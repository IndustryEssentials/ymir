import {
  getKeywords,
  updateKeywords,
  updateKeyword,
  getRecommendKeywords,
} from "../keyword"
import { product, products, requestExample } from './func'

describe("service: keywords", () => {
  it("getKeywords -> success -> filter name", () => {
    const params = { q: 'search name' }
    const expected = products(6)
    requestExample(getKeywords, params, { items: expected, total: expected.length }, 'get')
  })
  it("getKeywords -> success -> page", () => {
    const params = { limit: 20, offset: 40 }
    const expected = products(20)
    requestExample(getKeywords, params, { items: expected, total: expected.length }, 'get')
  })
  it("updateKeywords -> success", () => {
    const keywords = [{ name: 'cat', aliases: ['kitty'] }, { name: 'dog' }]
    const expected = 'success'
    requestExample(updateKeywords, { keywords }, expected, 'post')
  })
  it("updateKeywords -> success", () => {
    const keywords = [{ name: 'cat', aliases: ['kitty'] }, { name: 'dog' }]
    const expected = { failed: [] }
    requestExample(updateKeywords, { keywords, dry_run: true }, expected, 'post')
  })
  it("updateKeywords -> success -> nothing updated", () => {
    const expected = { failed: [] }
    requestExample(updateKeywords, {}, expected, 'post')
  })
  it("updateKeyword -> success", () => {
    const name = 'dog'
    const aliases = ['doggie', 'baby']
    const expected = { failed: [] }
    requestExample(updateKeyword, { name, aliases }, expected)
    requestExample(updateKeyword, { name: 'cat' }, expected)
  })
  it("getRecommendKeywords -> success -> by dataset ids", () => {
    const params = { dataset_ids: [1,2,4], limit: 5 }
    const expected = products(5)
    requestExample(getRecommendKeywords, params, expected, 'get')
  })
  it("getRecommendKeywords -> success -> by dataset ids", () => {
    const params = { limit: 8, global: true }
    const expected = products(8)
    requestExample(getRecommendKeywords, params, expected, 'get')
  })
})
