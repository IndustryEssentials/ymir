
import mockjs, { Random } from 'mockjs'

const result = mockjs.mock({
  code: 0, 
  'result|1-25': [{ docker_name: '@title(2, 5)', functions: '@title(1,3)', contributor: '@name', description: '@title(2,20)', organization: '@title(1,6)' }]
})

const detailResult = mockjs.mock({ code: 0, result: { 
  'id': 1002, name: '@title(2,4)', 'type|1': [1,2,9], url: '@string(4,20)', 
  'configs|2-3': [{ 'type|1': [1,2,9], config: { a: '@name'}, }],
  description: '@title(2,20)',
  is_shared: '@boolean',
  'state|1': [1,3,4],
}
})
const listResult = mockjs.mock({
  code: 0,
  result: {
    'items|1-20': [{ 
      'id|+1': 1002, name: '@title(2,4)', 'type|1': [1,2,9], url: '@string(4,20)', 
      'configs|1-3': [{ 'type|1': [1,2,9], config: { a: '@name'}, }],
      description: '@title(2,20)',
      is_shared: '@boolean',
      'state|1': [1,3,4],
    }],
    total: 14,
  }
})

export default {
  'GET /api/v1/images/shared': result,
  'GET /api/v1/images/': listResult,
  'GET /api/v1/images/1002': detailResult,
  // 'POST /api/v1/auth/token': {code: 0, result: {access_token: 'adfjasdhfasfldjasdlfkjad'}},
}
