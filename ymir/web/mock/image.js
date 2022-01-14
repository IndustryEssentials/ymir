
import mockjs, { Random } from 'mockjs'

const result = mockjs.mock({
  code: 0, 
  'result|1-25': [{ docker_name: '@title(2, 5)', functions: '@title(1,3)', contributor: '@name', description: '@title(2,20)', organization: '@title(1,6)' }]
})
export default {
  'GET /api/v1/images/shared': result
}
