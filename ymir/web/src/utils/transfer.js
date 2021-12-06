export function createFd(params) {
  let fd = new FormData()
  Object.keys(params).forEach((key) => {
    fd.append(key, params[key])
  })
  return fd
}
