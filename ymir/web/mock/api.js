const baseApi = (list = []) => {
  const apis = {}
  list.forEach(({ method = 'get', url = '', data = {}}) => apis[`${method} /api/v1/${url}`] = { code: 0, ...data })
  return apis
}

export default baseApi
