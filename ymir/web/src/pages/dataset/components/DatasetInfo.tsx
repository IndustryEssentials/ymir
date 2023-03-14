import { FC } from 'react'
import { Space, Tag } from 'antd'

import t from '@/utils/t'

import ObjectTypeTag from '@/components/project/ObjectTypeTag'
import VersionName from '@/components/result/VersionName'

const DatasetInfo: FC<{ dataset?: YModels.Dataset | YModels.Prediction; pred?: boolean }> = ({ dataset, pred }) => {
  return dataset ? (
    <Space wrap={true}>
      {!pred ? (
        <strong>
          <VersionName result={dataset} />
        </strong>
      ) : null}
      <span>{t('dataset.detail.pager.total', { total: dataset.assetCount })}</span>
      <ObjectTypeTag type={dataset.type} />
      {pred && dataset?.inferClass ? (
        <div>
          {t('dataset.detail.infer.class')}
          {dataset?.inferClass?.map((cls) => (
            <Tag key={cls}>{cls}</Tag>
          ))}
        </div>
      ) : null}
    </Space>
  ) : null
}

export default DatasetInfo
