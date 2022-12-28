import request from '@/utils/request'
import { TYPES } from '@/constants/image'

type QueryParams = {
  name?: string
  type?: number
  state?: TYPES
  url?: string
  limit?: number
  offset?: number
}
type Image = {
  name: string
  url: string
  description?: string
  enable_livecode?: boolean
}
type EditImage = Omit<Image, 'url'>
type ShareParams = {
  username: string
  email: string
  phone: string
  org: string
}

/** image service */
/**
 *
 * @param {number} id
 * @returns
 */
export function getImage(id: number) {
  return request.get(`images/${id}`)
}

/**
 * @param {*} params
 * { name, type, start_time = 0, end_time = 0, offset = 0, limit = 10, sort_by: 1|2 }
 * @returns
 */
export function getImages(params: QueryParams) {
  return request.get('images/', { params })
}

/**
 * delete image
 * @param {number} id
 * @returns
 */
export function delImage(id: number) {
  return request({
    method: 'delete',
    url: `/images/${id}`,
  })
}

/**
 * create a image
 * @param {object} image
 * {
 *   "hash": "string",
 *   "name": "string",
 *   "map": "string",
 *   "parameters": "string",
 *   "task_id": 0,
 *   "user_id": 0
 * }
 * @returns
 */
export function createImage(image: Image) {
  return request.post('/images/', image)
}

export function updateImage(id: number, { name, description }: EditImage) {
  return request({
    method: 'patch',
    url: `/images/${id}`,
    data: {
      name,
      description,
    },
  })
}

export function shareImage(id: number, { username, email, phone, org }: ShareParams) {
  return request.post(`/images/shared`, {
    docker_image_id: id,
    contributor: username,
    email,
    phone,
    organization: org,
  })
}

export function relateImage(id: number, relations: number[]) {
  return request({
    url: `/images/${id}/related`,
    method: 'PUT',
    data: {
      dest_image_ids: relations,
    },
  })
}

export function getShareImages() {
  return request.get('/images/shared')
}
