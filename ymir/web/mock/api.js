const baseApi = (list = []) => {
  const apis = {}
  list.forEach(({ method = 'get', url = '', data = {}}) => {
    // todo
    const rurl = typeof url === 'string' ? `${method} /api/v1/${url}` : new RegExp(`${method} /api/v1/${url}`)

    return apis[`${method} /api/v1/${url}`] = { code: 0, ...data }
  })
  return apis
}

export default baseApi
