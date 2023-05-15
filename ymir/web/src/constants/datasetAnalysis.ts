import { Suggestion } from './typings/dataset'

enum ClassBias {
  perfect = 1,
  good = 2,
  normal = 3,
  bad = 4,
}

enum AnnotationDensity {
  simple = 1,
  normal = 2,
  complex = 3,
}
enum AnnotationCount {
  perfect = 1,
  good = 2,
  normal = 3,
  bad = 4,
}
const transferSuggestion = (sug?: { [bounding: string]: string[] }, type?: string) => {
  if (!sug) {
    return
  }
  const bounding = Object.keys(sug)[0]
  const values = sug[bounding]
  const suggest: Suggestion = {
    bounding: Number(bounding),
    values,
    type,
  }
  return Number(bounding) ? suggest : undefined
}

export { ClassBias, AnnotationDensity, AnnotationCount, transferSuggestion }
