
import baseApi from './api.js'

export default baseApi([
  {
    url: 'sys_info/',
    data: {
      result: {
        gpu_count: 8,
      }
    }
  },
])
