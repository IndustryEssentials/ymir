import { FC } from 'react'
import t from '@/utils/t'

type Props = {
  suggestions?: YModels.DatasetSuggestions
}

const pStyle = { marginBottom: 0, lineHeight: 1.2 }
const SimpleSuggestion: FC<Props> = ({ suggestions }) =>
  suggestions ? (
    <div>
      {Object.keys(suggestions).map((key) => {
        const suggest = suggestions[key]
        const count = suggest?.values?.length
        return count ? (
          <p key={key} style={pStyle}>
            {t(`dataset.analysis.simple.suggest.${key}`, { count })}
          </p>
        ) : null
      })}
    </div>
  ) : null

export default SimpleSuggestion
