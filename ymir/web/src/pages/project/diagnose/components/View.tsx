import type { FC } from 'react'
import { ViewProps } from './common'

const View = (Component: FC<ViewProps>) => {
  const Viewer = (props: ViewProps) => {
    return <Component {...props} />
  }
  return Viewer
}

export default View
