class Storage {
  constructor() {}
  set(key, value) {
    localStorage.setItem(key, JSON.stringify(value))
  }
  get(key) {
    const data = localStorage.getItem(key)
    return JSON.parse(data)
  }
  remove(key) {
    localStorage.removeItem(key)
  }
}

export default new Storage()
