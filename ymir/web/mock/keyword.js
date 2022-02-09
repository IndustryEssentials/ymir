
import mockjs, { Random } from 'mockjs'
import baseApi from './api.js'
const kws = ["cat", "dog", "person", "car", "bottle", "bird", "pigeon", "fish",
  "new fish", "dophine", "root", "room", "house", "family", "coak", "old fish", "space",]
Random.extend({
  keywords: function (min = 2, max = 5) {
    const keywords = [...new Set(Random.range(1, Random.integer(min, max)).map(v => kws[Random.integer(0, kws.length - 1)]))]
    return keywords.map(key => ([key, Random.integer(1, 100)]))
  }
})

export const random = Random

export default baseApi([
  {
    url: 'stats/keywords/recommend',
    data: {
      result: Random.keywords(5)
    }
  },
  {
    url: 'stats/keywords/hot',
    data: {
      result: Random.keywords(5)
    }
  }
])
