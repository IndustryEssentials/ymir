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
        const values = suggest.values.filter((value) => suggest.type !== 'keyword' || !target?.length || target.includes(value)).join(', ')
        return (
          <Suggest
            key={key}
            title={t(`${label}.title`)}
            content={t(label, {
              bounding: suggest.bounding,
              boundingLabel: percent(suggest.bounding, 0),
              values,
            })}
          />
        )
      })}
    </div>
  ) : null
}

export default Suggestion
