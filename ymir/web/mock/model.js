
import mockjs, { Random } from 'mockjs'
import baseApi from './api.js'

Random.extend({
  allKeywords: ["cat", "dog", "person", "car", "bottle", "bird", "pigeon", "fish",
    "new fish", "dophine", "root", "room", "house", "family", "coak", "old fish", "space",],
  keywords: function () {
    return [...new Set(Random.range(1, Random.integer(2, 5)).map(v => this.allKeywords[Random.integer(0, this.allKeywords.length - 1)]))]
  }
})

const groups = mockjs.mock({
  'items|1-20': [{
    'id|+1': 4001,
    name: '@title(1,5)',
    createTime: '@datetime',
  }],
  total: 34,
})

const item = {
  'id|+1': 10001,
  name: "@title(2, 5)",
  "map|0-1": 0.0,
  keywords: "@keywords",
  type: 1,
  source: 1,
  task_name: "@title(1,2)",
  parameters: {
    include_train_datasets: [1, 3, 5],
    include_validation_datasets: [2],
    docker_image: 'asdfjaldsfkj',
    docker_image_id: 6,
  },
}

const models = mockjs.mock({
  'items|1-20': [item],
  total: 54,
})
export default baseApi([
  {
    url: 'model_groups/',
    data: {
      result: groups,
    }
  },
  {
    url: 'model_groups/4001',
    data: {
      result: models,
    }
  },
  {
    url: 'models/10008',
    data: {
      result: mockjs.mock(item),
    }
  },
])
