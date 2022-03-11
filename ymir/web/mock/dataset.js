
import mockjs from 'mockjs'
import { random } from './keyword'
import baseApi from './api.js'

const item = {
  "name": "@title(1,4)",
  "hash": "@string(32)",
  "type|1": [1,2,3,4,5],
  "state|1": [2,3],
  'version|1': [1,2,3,4,5,6,7,8],
  "asset_count": '@integer(2,9999)',
  "keyword_count": '@integer(1,30)',
  "task_id": '@integer(1000, 9999)',
  "create_datetime": "@datetime",
  "id|+1": 10001,
  "group_id|+1": 40001,
  "project_id": 30001,
  "keywords": '@keywords(2, 5)',
  "progress": '@integer(0,100)',
  "task_state|1": [1,2,3,4],
  "task_progress": '@integer(0,100)'
}

const list = mockjs.mock({
  'items|1-20': [item],
  total: 34,
})

const groups = mockjs.mock({
  'items|1-20': [{
    'id|+1': 40001,
    name: '@title(1,5)',
    createTime: '@datetime',
  }],
  total: 34,
})

export default baseApi([
  {
    url: 'dataset_groups/',
    data: {
      result: groups,
    }
  },
  {
    url: 'dataset_groups/40001',
    data: {
      result: list,
    }
  },
  {
    url: 'datasets/',
    data: {
      result: list,
    }
  },
  {
    url: 'datasets/10008',
    data: {
      result: mockjs.mock(item),
    }
  },
])
