export const deepClone = (obj: object) => JSON.parse(JSON.stringify(obj))

type obj = {
  [key: string]: any,
}
export const isSame = (obj1: obj, obj2: obj) => {
  const same = (o1:obj, o2: obj) => Object.keys(o1).every(key => o1[key] === o2[key])
  return same(obj1, obj2) && same(obj2, obj1)
}
