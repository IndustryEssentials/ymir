export const deepClone = (obj: object) => JSON.parse(JSON.stringify(obj))

type obj = {
  [key: string]: any
}
export const isSame = (obj1: obj, obj2: obj) => {
  const same = (o1: obj, o2: obj) =>
    Object.keys(o1).every((key) => o1[key] === o2[key])
  return same(obj1, obj2) && same(obj2, obj1)
}

/**
 * @description inspect const is plain object
 * @export
 * @param {*} obj object to inspect
 * @return {*}  {boolean}
 */
export function isPlainObject(obj: any): boolean {
  if (typeof obj !== "object" || obj === null) return false

  let proto = obj
  while (Object.getPrototypeOf(proto) !== null) {
    proto = Object.getPrototypeOf(proto)
  }

  return Object.getPrototypeOf(obj) === proto
}
