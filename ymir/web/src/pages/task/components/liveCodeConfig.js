
export const FIELDS = Object.freeze([
  { key: 'url', field: 'git_url', },
  { key: 'id', field: 'git_branch', },
  { key: 'config', field: 'code_config', },
])

export const getConfigUrl = (config = {}) => {
  const getField = index => config[FIELDS[index].field] || ''
  const base = getField(0).replace(/(\.git)?$/, '')
  const commit = getField(1)
  const configFile = getField(2)
  const url = `${base}/blob/${commit}/${configFile}`
  return url
}

export const isLiveCode = config => FIELDS.reduce((prev, curr) => prev && config[curr.field], true)

export function removeLiveCodeConfig(config = {}) {
  return Object.keys(config).reduce((prev, key) => FIELDS.map(({ field }) => field).includes(key) ?
    prev :
    {
      ...prev,
      [key]: config[key],
    }, {})
}