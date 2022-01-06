
import mockjs, { Random } from 'mockjs'
Random.extend({
  allKeywords: ["cat", "dog", "person", "car", "bottle", "bird", "pigeon", "fish", 
    "new fish", "dophine", "root", "room", "house", "family", "coak","old fish", "space",],
  keywords: function () {
    return [...new Set(Random.range(1, Random.integer(2, 5)).map(v => this.allKeywords[Random.integer(0, this.allKeywords.length - 1)]))]
  }
})

const models = mockjs.mock({
  'items|4-30': [{ 'id|+1': 10001, name: '@title(2, 5)', 'map|0-0.2': 0.00, 'keywords': '@keywords', type: 1, source: 1, task_name: '@title(1,2)' }],
})
export default {
  'GET /api/v1/models/': { code: 0, result: {
    ...models,
    total: models.items.length,
  }}
}