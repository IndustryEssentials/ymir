import { Empty } from "antd"

import nodataImg from '@/assets/nodata.png'

export default (props) => (
  <Empty image={nodataImg} imageStyle={{ height: 100 }} {...props} />
)