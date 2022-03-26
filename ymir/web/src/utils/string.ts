import { randomNumber } from './number'

export function generateName(prefix: string = '', len: number = 20) {
  const r = `_${randomNumber()}`
  return prefix.charAt(len - 8) ? prefix.replace(new RegExp(`(^\\w{${len - 8}}).*$`), `$1${r}`) : prefix + r
}