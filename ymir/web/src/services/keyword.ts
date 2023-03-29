import request from '@/utils/request'
import { KeywordObjectType, KeywordsQueryParams, KeywordsUpdateParams, RecommendKeywordsQueryParams } from './keyword.d'
/** keyword service */

/**
 * @description get keywords by query params
 * @export
 * @param {KeywordsQueryParams} params
 */
export function getKeywords(params: KeywordsQueryParams) {
  return request.get('keywords/', { params })
}

/**
 * new and update keywords
 * @param {array} keywords
 * @param {boolean} dry_run only check, fake update
 * @returns
 */
/**
 * @description update keywords, dry run is optional, default as false
 * @export
 * @param {KeywordsUpdateParams} { keywords, dry_run = false }
 */
export function updateKeywords({ keywords, dry_run = false }: KeywordsUpdateParams) {
  return request.post('/keywords/', {
    keywords,
    dry_run,
  })
}

export function checkDuplication(keywords: string[] = []) {
  return request.post('/keywords/check_duplication', {
    keywords: keywords.map((keyword) => ({ name: keyword })),
  })
}

/**
 * update keyword
 * @param {string} name
 * @param {array} [aliases]
 * @returns
 */
/**
 * @description update single keyword
 * @export
 * @param {KeywordObjectType} { name, aliases = [] }
 */
export function updateKeyword({ name, aliases = [] }: KeywordObjectType) {
  return request({
    method: 'PATCH',
    url: `/keywords/${name}`,
    data: {
      aliases,
    },
  })
}

/**
 * @description get recommend keywords of dataset or global
 * @export
 * @param {RecommendKeywordsQueryParams} { dataset_ids = [], limit, global = false }
 * @return {Promise}
 */
export function getRecommendKeywords({ dataset_ids = [], limit, global = false }: RecommendKeywordsQueryParams) {
  if (!global) {
    return request.get(`/stats/keywords/recommend`, { params: { dataset_ids: dataset_ids.toString(), limit } })
  } else {
    return request.get('/stats/keywords/hot', { params: { limit } })
  }
}
