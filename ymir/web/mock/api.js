const baseApi = (list = []) => {
  const apis = {}
  list.forEach(({ method = 'get', url = '', data = {}}) => {
    const rurl = typeof url === 'string' ? `${method} /api/v1/${url}` : url

    return apis[rurl] = { code: 0, ...data }
  })
  return apis
}

export default baseApi
