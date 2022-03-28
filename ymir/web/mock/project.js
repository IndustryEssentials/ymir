
import mockjs, { Random } from 'mockjs'
import baseApi from './api.js'

const item = {
  'id|+1': 2001,
  'chunk_size': '@integer(1,100)',
  training_type: 1,
  iteration_target: '@integer(1,20)',
  map_target: '@integer(40,99)',
  training_dataset_count_target: '@integer(0, 1000000000)',
  name: '@title(2,4)',
  'training_keywords': Random.keywords(2, 5),
  train_set: '@integer(10001,29999)',
  test_set: '@integer(10001,29999)',
  mining_set: '@integer(10001,29999)',
  set_account: '@integer(0,100)',
  models_account: '@integer(0,100)',
  flag: {
    type: '@string(3,7)',
    value: '@integer(4,6)',
  },
  'mining_strategy|1': [1,2,3],
  current_iteration: {
    'id|+1': 3001,
    'name': 'V@integer(1,10)',
    'version': '@integer(1,10)',
    'current_step': '@integer(1,6)',
    'train_set': '@integer(4001, 5000)',
    'train_update_result': '@integer(5001, 6000)',
    'mining_result|': '@integer(6001,7000)',
    'label_set|': '@integer(7001, 8000)',
    'mining_set|': '@integer(8001, 9000)',
    'model|': '@integer(9001,9999)',
  },
  create_datetime: '@datetime',
  description: '@title(1,20)',
}

const list  = mockjs.mock({
  'items|1-20': [item],
  total: 29,
})

export default baseApi([
  {
    url: 'projects/',
    data: {
      result: list,
    }
  },
  {
    url: 'projects/2001',
    data: {
      result: mockjs.mock({ ...item, id: 2001 }),
    }
  }
])
