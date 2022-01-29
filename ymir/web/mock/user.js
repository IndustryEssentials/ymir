
import baseApi from './api.js'

export default baseApi([
  {
    url: 'auth/token',
    method: 'POST',
    data: {
      result: {
        access_token: 'adha;djfka;dfja;dfjasdkfdghdkf',
      }
    }
  },
])
