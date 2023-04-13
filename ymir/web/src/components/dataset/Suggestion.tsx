import { FC } from 'react'
import t from '@/utils/t'
import { percent } from '@/utils/number'

type Props = {
  suggestions?: YModels.DatasetSuggestions
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

const Suggestion: FC<Props> = ({ suggestions, target }) => {
  return suggestions ? (
    <div>
      {Object.keys(suggestions).map((key) => {
        const suggest = suggestions[key]
        const label = `dataset.analysis.suggestion.${key}`
        return <Suggest key={key} title={t(`${label}.title`)} content={t(label, {
          bounding: suggest.bounding,
          boundingLabel: percent(suggest.bounding, 0),
          values: suggest.values.filter(value => !target?.length || target.includes(value)).join(', ')
        })} />
      })}
    </div>
  ) : null
}

export default Suggestion
