class Storage {
  constructor() {}
  set(key: string, value: any) {
    localStorage.setItem(key, JSON.stringify(value))
  }
  get(key: string) {
    const data = localStorage.getItem(key)
    return data ? JSON.parse(data) : data
  }
  remove(key: string) {
    localStorage.removeItem(key)
  }
}

export default new Storage()
