import { Spin } from 'antd'
import { FC } from 'react'

const DataLoading: FC = () => {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        width: '100%',
        minHeight: 300
      }}
    >
      <Spin size="large" />
    </div>
  )
}

export default DataLoading
