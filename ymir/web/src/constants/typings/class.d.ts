type Classes = string[]

type ClassObject = { name: string; aliases?: string[] }

type ClassesCount = {
  [key: string]: number
}

type CustomClass = {
  [key: string]: string | number
}

export { Classes, ClassObject, ClassesCount, CustomClass }
