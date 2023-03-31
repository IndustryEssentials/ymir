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
}
type Image = {
  name: string
  url: string
  description?: string
  enable_livecode?: boolean
}
type EditImage = Omit<Image, 'url'>


export { QueryParams, Image, EditImage }