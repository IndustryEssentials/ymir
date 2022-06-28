
import mockjs, { Random } from 'mockjs'
import { random } from './keyword'
import baseApi from './api.js'

const item = {
  "name": "@title(1,4)",
  "hash": "@string(32)",
  "type|1": [1, 2, 3, 4, 5],
  "state|1": [2, 3],
  'version|1': [1, 2, 3, 4, 5, 6, 7, 8],
  "asset_count": '@integer(2,9999)',
  "keyword_count": '@integer(1,30)',
  "task_id": '@integer(1000, 9999)',
  "create_datetime": "@datetime",
  "id|+1": 10001,
  "group_id|+1": 40001,
  "project_id": 30001,
  "keywords": '@keywords(2, 5)',
  "progress": '@integer(0,100)',
  "task_state|1": [1, 2, 3, 4],
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

const xyz = {
  x: '@float(0, 1, 0, 4)',
  y: '@float(0, 1, 0, 4)',
  z: '@float(0, 1, 0, 4)',
}
const metadata = {
  "ap": '@float(0, 1, 0, 4)',
  "ar": '@float(0, 1, 0, 4)',
  "tp": '@float(0, 1, 0, 4)',
  "fp": '@float(0, 1, 0, 4)',
  "fn": '@float(0, 1, 0, 4)',
  "pr_curve|1-20": [xyz],
}

const ci = kws => kws.reduce((prev, kw) => ({
  ...prev,
  [kw]: metadata,
}), {})
const ck = cks => cks.reduce((prev, { value, sub }) => ({
  ...prev,
  [value]: {
    total: metadata,
    sub: sub.reduce((prev, kw) => ({ ...prev, [kw]: metadata }), {})
  }
}), {})
const dsData = () => ({
  conf_thr: '@float(0, 1, 0, 4)',
  iou_evaluations: {
    [Random.float(0, 1)]: {
      ci_evaluations: ci(['person', 'cat']),
      ck_evaluations: ck([{ value: 'day', sub: ['rainy', 'sunny'] }, { value: 'color', sub: ['black', 'white'] }]),
    },
  },
})

const datasets = [80, 81]
const evaluation = mockjs.mock(datasets.reduce((prev, id) => ({
  ...prev,
  [id]: dsData(),
}), {}))

export default baseApi([
  // {
  //   url: 'dataset_groups/',
  //   data: {
  //     result: groups,
  //   }
  // },
  // {
  //   url: 'dataset_groups/40001',
  //   data: {
  //     result: list,
  //   }
  // },
  // {
  //   url: 'datasets/',
  //   data: {
  //     result: list,
  //   }
  // },
  // {
  //   url: 'datasets/10008',
  //   data: {
  //     result: mockjs.mock(item),
  //   }
  // },
  {
    method: 'post',
    url: 'datasets/evaluation',
    data: {
      result: evaluation,
    }
  }
])
