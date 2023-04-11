import { AnnotationCount, AnnotationDensity, ClassBias } from '@/constants/datasetAnalysis'
import t from '@/utils/t'
import { FC, useEffect, useState } from 'react'

type Props = {
  metrics?: YModels.DatasetMetrics
  target?: string[]
}

const Suggest: FC<{ title?: string; content?: string }> = ({ title, content }) => {
  return (
    <>
      <h4>{title}</h4>
      <p>{content}</p>
    </>
  )
}

const Suggestion: FC<Props> = ({ metrics, target }) => {
  const [aclasses, setAclasses] = useState<string[]>([])
  const [cclasses, setCclasses] = useState<string[]>([])
  const [simple, setSimple] = useState(false)

  useEffect(() => {
    if (!metrics) {
      return
    }
    setAclasses(calClasses(metrics.annotationCount, AnnotationCount.bad, target))
    setCclasses(calClasses(metrics.classBias, ClassBias.bad, target))
    setSimple(metrics.annotationDensity === AnnotationDensity.simple)
  }, [metrics])

  return metrics ? (
    <div>
      {aclasses.length ? (
        <Suggest
          title={t('dataset.analysis.suggestion.annotationCount.title')}
          content={t('dataset.analysis.suggestion.annotationCount', { classes: aclasses.join(', ') })}
        />
      ) : null}
      {cclasses.length ? (
        <Suggest
          title={t('dataset.analysis.suggestion.classBias.title')}
          content={t('dataset.analysis.suggestion.classBias', { classes: aclasses.join(', ') })}
        />
      ) : null}

      {simple ? (
        <Suggest title={t('dataset.analysis.suggestion.annotationDensity.title')} content={t('dataset.analysis.suggestion.annotationDensity')} />
      ) : null}
    </div>
  ) : null
}

const calClasses = (countObject: YModels.classMetric = {}, level: number, classes?: string[]) => {
  return Object.keys(countObject).reduce<string[]>(
    (prev, curr) => (countObject[curr] === level && (!classes?.length || classes.includes(curr)) ? [...prev, curr] : prev),
    [],
  )
}

export default Suggestion
