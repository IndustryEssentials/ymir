import { FC } from "react"
type Props = {
  keywords?: string[],
  len?: number,
}

const KeywordsItem: FC<Props> = ({ keywords = [], len = 5 }) => {
  const kws = keywords.length > len ? [...keywords.slice(0, len), '...'] : keywords
  return <span title={keywords.join(',')}>{kws.join(',')}</span>
}

export default KeywordsItem
