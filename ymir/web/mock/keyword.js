
import mockjs, { Random } from 'mockjs'
import baseApi from './api.js'
const kws = ["cat", "dog", "person", "car", "bottle", "bird", "pigeon", "fish",
  "new fish", "dophine", "root", "room", "house", "family", "coak", "old fish", "space",]
Random.extend({
  keywords: function (min = 2, max = 5) {
    return [...new Set(Random.range(1, Random.integer(min, max)).map(v => kws[Random.integer(0, kws.length - 1)]))]
  }
})

export const random = Random

const keywords = mockjs.mock({
  'items|0-100': [{ name: '@title(1,2)', aliases: []}],
  total: '@integer(1,100)'
})

export default baseApi([
  {
    url: 'keywords/',
    data: {
      result: keywords,
    }
  },
  {
    url: 'stats/keywords/recommend',
    data: {
      result: Random.keywords(5).map(key => ([key, Random.integer(1, 100)]))
    }
  },
  {
    url: 'stats/keywords/hot',
    data: {
      result: Random.keywords(5).map(key => ([key, Random.integer(1, 100)]))
    }
  }
])
