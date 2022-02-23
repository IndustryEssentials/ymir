
import mockjs, { Random } from 'mockjs'
import baseApi from './api.js'

const item = {
  "name": "@title(1,4)",
  "hash": "@string(32)",
  "type|1": [1,2,3,4,5],
  "state|1": [1,2,3,4],
  "asset_count": '@integer(2,9999)',
  "keyword_count": Random.integer(1,30),
  "user_id": Random.integer(1, 200),
  "task_id": '@integer(1000, 9999)',
  "is_deleted": false,
  "create_datetime": "@datetime",
  "update_datetime": "@datetime",
  "id|+1": 10001,
  "parameters": {},
  "config": {},
  "keywords": [],
  "ignored_keywords": [],
  "source": 5,
  "progress": '@integer(0,100)',
  "task_name": "@string(3,30)",
  "task_state|1": [1,2,3,4],
  "task_progress": '@integer(0,100)'
}

const list = mockjs.mock({
  'items|1-20': [item],
  total: 34,
})

export default baseApi([
  {
    url: 'datasets/',
    data: {
      result: list,
    }
  },
  {
    url: /datasets\/\d+/,
    data: {
      result: item,
    }
  },
])
