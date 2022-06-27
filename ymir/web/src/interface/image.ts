export interface InferConfig {
  type: number,
  config: {
    [key: string]: any,
  },
}
export interface Image {
  id: number,
  name: string,
  state: number,
  isShared: boolean,
  functions:Array<number>,
  configs: Array<InferConfig>,
  url: string,
  liveCode?: boolean,
  description: string,
  createTime: string,
  related?: Array<Image>,
}
