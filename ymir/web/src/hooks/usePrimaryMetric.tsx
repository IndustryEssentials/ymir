import { FC } from 'react'
import { getPrimaryMetricsLabel } from '@/constants/model'
import { ObjectType } from '@/constants/objectType'
import { percent } from '@/utils/number'
import t from '@/utils/t'

export type TemplateProps = { metricLabel: string; metric: number; percent: string }

const usePrimaryMetric = <P extends {} = {}>(ContentComponent: FC<TemplateProps>) => {
  const Render: FC<{ primaryMetric?: number; type: ObjectType } & P> = ({ primaryMetric = 0, type, ...props }) => {
    const label = t(getPrimaryMetricsLabel(type))
    const cent = percent(primaryMetric) || ''
    return label && primaryMetric ? <ContentComponent {...props} metricLabel={label} metric={primaryMetric} percent={cent} /> : null
  }

  return Render
}

export default usePrimaryMetric
