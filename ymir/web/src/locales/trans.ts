import { LangItem, LangItems } from './interface'

export default function trans(obj : LangItems, lang : string = 'cn') {
  const result: LangItem = {}
  for(let key in obj) {
    const item = obj[key]
    result[key] = item[lang]
  }
  return result
}