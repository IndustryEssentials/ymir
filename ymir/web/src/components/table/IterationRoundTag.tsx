import { FC, useState, useEffect, useCallback } from 'react'
import t from '@/utils/t'
import { Iteration } from '@/constants'
type Props = {
  id: number
  iterations?: Iteration[]
  model?: boolean
}

const extraIterTag = {
  padding: '2px 8px',
  fontSize: '12px',
  color: '@primary-color',
  backgroundColor: 'rgba(54, 203, 203, 0.08)',
}

const IterationRoundTag: FC<Props> = ({ iterations, id, model }) => {
  const [label, setLabel] = useState<string>('')
  const [iterationResults, setIterationResults] = useState<{ [id: number]: number }>({})

  useEffect(() => {
    const maps: { [key: number]: number } = {}
    iterations?.forEach(({ steps, round }) =>
      (model ? [steps[steps.length - 1]] : steps.slice(0, steps.length - 1)).map(({ resultId }) => resultId).forEach((id) => id && (maps[id] = round)),
    )
    setIterationResults(maps)
  }, [iterations])

  useEffect(() => {
    setLabel(getIterationLabel(id))
  }, [iterationResults, id])

  const getIterationLabel = useCallback(
    (id: number) => {
      const round = iterationResults[id]
      if (round) {
        return t('iteration.tag.round', { round })
      }
    },
    [iterationResults],
  )

  return label ? <div style={extraIterTag}>{label}</div> : null
}
export default IterationRoundTag
