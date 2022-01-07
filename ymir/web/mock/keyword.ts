
import mockjs, { Random } from 'mockjs'
import baseApi from './api'
const kws : string[] = ["cat", "dog", "person", "car", "bottle", "bird", "pigeon", "fish", 
    "new fish", "dophine", "root", "room", "house", "family", "coak","old fish", "space",]
Random.extend({
  allKeywords: () => kws,
  keywords: function (min = 2, max = 5) {
    const itemKey = Random.integer(0, this.allKeywords.length - 1)
    return [...new Set(Random.range(1, Random.integer(min, max)).map(v => this.allKeywords()[itemKey]))]
  }
})

export const random = Random

export default baseApi({
  url: 'keywords/recommand',
  data: {
    result: Random.keywords(3, 8)
  }
})
