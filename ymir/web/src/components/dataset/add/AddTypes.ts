export enum Types {
  INTERNAL = 1,
  COPY = 2,
  NET = 3,
  LOCAL = 4,
  PATH = 5,
}

export function isType(type: Types) {
  return type === Types.COPY
}