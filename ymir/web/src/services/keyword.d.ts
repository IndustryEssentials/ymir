export type KeywordObjectType = {
  name: string
  aliases?: string[]
}
export type Keywords = string[]
export type KeywordsQueryParams = {
  q?: string
  offset?: number
  limit?: number
}
export type KeywordsUpdateParams = {
  keywords: KeywordObjectType,
  dry_run?: boolean
}
export type RecommendKeywordsQueryParams = {
  dataset_ids: number[]
  limit?: number
  global?: boolean
}
