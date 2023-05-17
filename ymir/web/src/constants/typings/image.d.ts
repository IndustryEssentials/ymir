import { ObjectType } from '../objectType'

type ImageConfig = { [key: string]: number | string }
type DockerImageConfig = {
  type: number
  config: ImageConfig
  object_type: ObjectType
}
type Image = {
  id: number
  name: string
  state: number
  functions: number[]
  configs: DockerImageConfig[]
  objectTypes: ObjectType[]
  url: string
  description: string
  createTime: string
  official: boolean
  related?: Array<Image>
  liveCode?: boolean
  errorCode?: string
  isSample?: boolean
}

export { ImageConfig, Image, DockerImageConfig }
