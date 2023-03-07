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
export function getAssets({ pid, id, type = 'keywords', keywords = [], cm = [], exclude = [], annoType = 1, offset = 0, limit = 20 }: YParams.AssetQueryParams) {
  return request.get(`/assets/`, {
    params: {
      project_id: pid,
      data_id: id,
      data_type: annoType,
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
export function getAsset(hash: string, pid: number, id: number, type = 1): Promise<AxiosResponse> {
  return request.get(`/assets/${hash}`, {
    params: {
      project_id: pid,
      data_id: id,
      data_type: type,
    }
  })
}
