export default KeywordsItem = ({ keywords = [], len = 5 }) => {
  const kws = keywords.length > len ? [...keywords.slice(0, len), '...'] : keywords
  return <span title={keywords.join(',')}>{kws.join(',')}</span>
}