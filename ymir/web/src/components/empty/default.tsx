import type { FC } from 'react'
import { Empty, EmptyProps } from 'antd'

import nodataImg from '@/assets/nodata.png'

const DefaultEmpty: FC<EmptyProps> = (props) => <Empty image={nodataImg} imageStyle={{ height: 100 }} {...props} />

export default DefaultEmpty
