const baseApi = ({ method = 'get', url = '', data = {} }) => {
  return { [`${method} /api/v1/${url}`]: { code: 0, ...data } }
}

export default baseApi
