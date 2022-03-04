
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
  {
    url: 'users/me',
    data: {
      result: {
        username: 'Leader',
        email: 'test@leader.com',
        phone: '18888888888',
        role: 3,
      }
    }
  },
])
