import { ColumnType } from 'antd/lib/table'

import StrongTitle from './StrongTitle'
import { default as ActionList } from '../Actions'

function Actions<T extends YModels.Result>(getActions: (record: T) => YComponents.Action[], showCount = 3): ColumnType<T> {
  return {
    title: <StrongTitle label="model.column.action" />,
    dataIndex: 'action',
    render: (_, record) => {
      const actions = getActions(record)
      return <ActionList actions={actions} showCount={showCount} />
    },
    align: 'center',
    width: '280px',
  }
}

export default Actions
