export function removeLiveCodeConfig(config = {}) {
  return Object.keys(config).reduce((prev, key) => [
    'git_url',
    'git_branch',
    'code_config',
  ].includes(key) ? prev : {
    ...prev,
    [key]: config[key],
  }, {})
}