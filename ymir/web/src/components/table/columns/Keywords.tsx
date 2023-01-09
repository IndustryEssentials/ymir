import { ColumnType } from 'antd/lib/table'
import { Tooltip } from 'antd'

import StrongTitle from './StrongTitle'
import t from '@/utils/t'
import { validDataset } from '@/constants/dataset'

function Keywords<T extends YModels.Dataset>(): ColumnType<T> {
  return {
    title: <StrongTitle label="dataset.column.keyword" />,
    dataIndex: 'keywords',
    render: (_, record) => {
      const { gt, pred } = record
      const renderLine = (keywords: string[] = [], label = 'gt') => (
        <div>
          <div>{t(`annotation.${label}`)}:</div>
          {t('dataset.column.keyword.label', {
            keywords: keywords.join(', '),
            total: keywords.length,
          })}
        </div>
      )
      const label = (
        <>
          {renderLine(gt?.keywords)}
          {renderLine(pred?.keywords, 'pred')}
        </>
      )
      return validDataset(record) ? (
        <Tooltip title={label} color="white" overlayInnerStyle={{ color: 'rgba(0,0,0,0.45)', fontSize: 12 }} mouseEnterDelay={0.5}>
          <div>{label}</div>
        </Tooltip>
      ) : null
    },
    ellipsis: {
      showTitle: false,
    },
  }
}

export default Keywords
