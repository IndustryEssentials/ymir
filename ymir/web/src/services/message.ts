import request from '@/utils/request'
import { QueryParams } from './typings/message.d'

/** message service */
/**
 * get single message by id
 * @param {number} id
 * @returns
 */
export function getMessage(id: number) {
  return request.get(`/messages/${id}`)
}

/**
 * @description get messages by query
 * @export
 * @param {QueryParams} params
 */
export function getMessages(params?: QueryParams) {
  const { pid, offset = 0, limit = 5, desc, startTime, endTime } = params || {}
  return request.get('/messages/', {
    params: {
      project_id: pid,
      limit,
      offset,
      start_time: startTime,
      end_time: endTime,
      desc,
    },
  })
}

/**
 * mark message readed
 * @param {number} id
 * @returns
 */
export function readMessage(id: number) {
  return request({
    method: 'patch',
    url: `/messages/${id}`,
    data: {
      is_read: true,
    }
  })
}
