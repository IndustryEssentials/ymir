import { randomNumber } from './number'

export function generateName(prefix: string = '', len: number = 20) {
  const r = `_${randomNumber()}`
  return prefix.charAt(len - 7) ? prefix.replace(new RegExp(`(^\\w{${len - 7}}).*$`), `$1${r}`) : prefix + r
}

type ob = {
  [key: string]: any,
}
export function templateString(str: string, obj: ob = {}) {
  return str.replace(/\{(\w+)\}/g, (reg, variable: string) => {
    return typeof obj[variable] !== 'undefined' && obj[variable] !== null ? obj[variable] : ''
  })
}

export function string2Array(str: string, seprate = ',') {
  if (!str) {
    return
  }
  const arr = str.split(seprate)
  return arr.map(item => Number.isNaN(Number(item)) ? item : Number(item)).filter(i => i)
}

export const getRandomRGB = (level = 1) => {
  const units = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
  const random = (list: Array<string>) => {
    const index = Math.floor(Math.random() * list.length / level) * level
    return list[index]
  }
  return `#${random(units)}${random(units)}${random(units)}`
}
