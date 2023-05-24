export enum Types {
  INTERNAL = 1,
  COPY = 2,
  NET = 3,
  LOCAL = 4,
  PATH = 5,
}

const typesLabel = {
  [Types.LOCAL]: 'local',
  [Types.NET]: 'net',
  [Types.PATH]: 'path',
  [Types.COPY]: 'copy',
  [Types.INTERNAL]: 'internal',
}

export const getTypeLabel = (type: Types, prefix: boolean = true) => `${prefix ? 'dataset.add.types.' : ''}${typesLabel[type]}`
