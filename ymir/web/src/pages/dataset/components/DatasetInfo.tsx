import { FC } from 'react'
import { Space, Tag } from 'antd'

import t from '@/utils/t'

import ObjectTypeTag from '@/components/project/ObjectTypeTag'
import VersionName from '@/components/result/VersionName'

const DatasetInfo: FC<{ dataset?: YModels.Prediction | YModels.Dataset }> = ({ dataset }) => {
  if (!dataset) {
    return null
  }
  const pred = 'pred' in dataset
  const inferClass = pred ? dataset?.inferClass : []
  return (
    <Space wrap={true}>
      {!pred ? (
        <strong>
          <VersionName result={dataset} />
        </strong>
      ) : null}
      <span>{t('dataset.detail.pager.total', { total: dataset.assetCount })}</span>
      <ObjectTypeTag type={dataset.type} />
      {pred && inferClass ? (
        <div>
          {t('dataset.detail.infer.class')}
          {inferClass?.map((cls) => (
            <Tag key={cls}>{cls}</Tag>
          ))}
        </div>
      ) : null}
    </Space>
  )
}

export default DatasetInfo
