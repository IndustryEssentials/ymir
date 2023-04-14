import { FC } from 'react'
import t from '@/utils/t'
import { getProjectTypeLabel } from '@/constants/objectType'
import Config from './Config'
import { Card } from 'antd'

const Configs: FC<{ configs?: YModels.DockerImageConfig[] }> = ({ configs = [] }) => {
  const groupByObjectType = Object.values(
    configs.reduce<{ [key: number]: YModels.DockerImageConfig[] }>((prev, curr) => {
      const list = prev[curr.object_type] ? [...prev[curr.object_type], curr] : [curr]
      return { ...prev, [curr.object_type]: list }
    }, {}),
  )
  return (
    <div>
      {groupByObjectType.map((configs, index) => {
        const objectType = configs[0].object_type
        return (
          <Card key={index} title={t(getProjectTypeLabel(objectType, true))} bordered={false} style={{ marginBottom: 10 }}>
            <Config configs={configs} />
          </Card>
        )
      })}
    </div>
  )
}

export default Configs
