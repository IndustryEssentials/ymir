type ActionType = 'label' | 'merge' | 'filter' | 'copy' | 'edit' | 'del' | 'train' | 'inference' | 'mining' | 'rerun' | 'stop'

const sequences: { [key: number]: ActionType[] } = {
  [0]: ['label', 'merge', 'filter', 'copy', 'edit', 'rerun', 'stop', 'del'],
  [1]: ['label', 'merge', 'filter', 'copy', 'edit', 'rerun', 'stop', 'del'],
  [2]: ['merge', 'filter', 'copy', 'label', 'edit', 'rerun', 'stop', 'del'],
  [4]: ['label', 'merge', 'filter', 'copy', 'edit', 'rerun', 'stop', 'del'],
  [1 + 2]: ['train', 'merge', 'filter', 'label', 'copy', 'edit', 'rerun', 'stop', 'del'],
  [1 + 4]: ['mining', 'label', 'inference', 'merge', 'filter', 'label', 'copy', 'edit', 'rerun', 'stop', 'del'],
  [2 + 4]: ['merge', 'filter', 'label', 'copy', 'edit', 'rerun', 'stop', 'del'],
  [1 + 2 + 4]: ['inference', 'train', 'merge', 'mining', 'filter', 'label', 'copy', 'edit', 'rerun', 'stop', 'del'],
  [1 + 2 + 4 + 8]: ['merge', 'copy', 'filter', 'label', 'train', 'mining', 'inference', 'edit', 'rerun', 'stop', 'del'],
}


const getSequence = (hasImages: boolean, haveAnnotations: boolean, haveModels: boolean, isRelatedDataset?: boolean) => {
  const ic = hasImages ? 1 : 0
  const ac = haveAnnotations ? 2 : 0
  const mc = haveModels ? 4 : 0
  const rc = isRelatedDataset ? 8 : 0
  const key = ic + ac + mc + rc
  return sequences[key]
}

const getActions = (
  actsObject: { [key: string]: YComponents.Action },
  { hasImages, haveAnnotations, haveModels, isRelatedDataset }: { [key: string]: boolean },
): YComponents.Action[] => {
  const seq = getSequence(hasImages, haveAnnotations, haveModels, isRelatedDataset)
  return seq.map((key) => actsObject[key])
}

export { getActions }
