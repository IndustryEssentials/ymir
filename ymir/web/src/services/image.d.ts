import { TYPES } from '../constants/image'
import { ObjectType } from '../constants/project'

type QueryParams = {
  name?: string
  type?: number
  objectType?: ObjectType
  state?: TYPES
  url?: string
  limit?: number
  offset?: number
  official?: boolean
}
type Image = {
  name: string
  url: string
  description?: string
  enable_livecode?: boolean
  is_official?: boolean
}
type EditImage = Omit<Image, 'url'>


export { QueryParams, Image, EditImage }