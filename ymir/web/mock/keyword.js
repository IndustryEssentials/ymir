
import mockjs, { Random } from 'mockjs'
import baseApi from './api.js'
const kws = ["cat", "dog", "person", "car", "bottle", "bird", "pigeon", "fish", 
    "new fish", "dophine", "root", "room", "house", "family", "coak","old fish", "space",]
Random.extend({
  keywords: function (min = 2, max = 5) {
    return [...new Set(Random.range(1, Random.integer(min, max)).map(v => kws[Random.integer(0, this.allKeywords.length - 1)]))]
  }
})

export const random = Random

export default baseApi({
  url: 'keywords/recommand/',
  data: {
    result: Random.keywords(3, 8)
  }
})
