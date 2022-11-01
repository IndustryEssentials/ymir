export type ImageConfig ={ [key: string]: number | string,}
export type DockerImageConfig = {
  type: number,
  config: ImageConfig,
}
export interface Image {
  id: number,
  name: string,
  state: number,
  isShared: boolean,
  functions:Array<number>,
  configs: Array<DockerImageConfig>,
  url: string,
  liveCode?: boolean,
  description: string,
  createTime: string,
  related?: Array<Image>,
}
