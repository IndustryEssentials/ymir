import request from '@/utils/request'
import { AxiosResponse } from 'axios'

/** asset service */

/**
 * @description get assets of dataset
 * @export
 * @param {AssetQueryParams} {
 *   id,
 *   type = 'keywords',
 *   keywords = [],
 *   cm = [],
 *   annoType = [],
 *   offset = 0,
 *   limit = 20,
 * }
 */
export function getAssets({ id, type = 'keywords', keywords = [], cm = [], exclude = [], annoType = [], offset = 0, limit = 20 }: YParams.AssetQueryParams) {
  return request.get(`datasets/${id}/assets`, {
    params: {
      [type]: keywords.toString() || undefined,
      in_cm_types: cm.toString() || undefined,
      ex_cm_types: exclude.toString() || undefined,
      annotation_types: annoType.toString() || undefined,
      offset,
      limit,
    },
  })
}

/**
 * @description get asset
 * @export
 * @param {number} id
 * @param {string} hash
 */
export function getAsset(id: number, hash: string): Promise<AxiosResponse> {
  return request.get(`datasets/${id}/assets/${hash}`)
}
