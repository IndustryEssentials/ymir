import { FC, useEffect, useState } from 'react'
import { AnnotationCount, ClassBias } from '@/constants/datasetAnalysis'
import t from '@/utils/t'

type Props = {
  metrics?: YModels.DatasetMetrics
}

const pStyle = { marginBottom: 0, lineHeight: 1.2 }
const SimpleSuggestion: FC<Props> = ({ metrics }) => {
  const [acount, setAcount] = useState(0)
  const [ccount, setCcount] = useState(0)
  useEffect(() => {
    metrics?.classBias && setCcount(calTotal(metrics?.classBias, ClassBias.bad))
    metrics?.annotationCount && setAcount(calTotal(metrics?.annotationCount, AnnotationCount.bad))
  }, [metrics])
  return metrics ? (
    <div>
      {acount ? <p style={pStyle}>{t(`dataset.analysis.simple.suggest.annotationCount`, { count: acount })}</p> : null}
      {ccount ? <p style={pStyle}>{t(`dataset.analysis.simple.suggest.classBias`, { count: ccount })}</p> : null}
      {metrics.annotationDensity ? (
        <p style={pStyle}>
          {t(`dataset.analysis.simple.suggest.annotationDensity`, {
            level: t(`dataset.analysis.annotationDensity.${metrics.annotationDensity}`),
          })}
        </p>
      ) : null}
    </div>
  ) : null
}

const calTotal = (countObject: YModels.classMetric, level: number) => {
  return Object.values(countObject).filter((n) => n === level).length
}
export default SimpleSuggestion
