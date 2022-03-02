
import mockjs, { Random } from 'mockjs'
import baseApi from './api.js'

const list  = mockjs.mock({
  'items|1-20': [{
    'id|+1': 2001,
    name: '@title(2,4)',
    'keywords': Random.keywords(2, 5),
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
    mining_block: '@integer(100,19999)',
    current_interation: {
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
  }],
  total: 29,
})

const groupItem = {
  'id|+1': 3001,
  'name': '@title(1,5)',
  create_datetime: '@datetime'
}

const datasetGroup = mockjs.mock({
  'items|1-20': [groupItem],
  total: 74,
})

export default baseApi([
  {
    url: 'projects/',
    data: {
      result: list,
    }
  },
  {
    url: 'projects/2001/datasets',
    data: {
      result: datasetGroup
    }
  }
])
