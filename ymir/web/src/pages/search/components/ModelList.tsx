import { FC } from 'react'
import { useEffect, useState, useRef } from 'react'
import { Table, TableProps } from 'antd'

import useRequest from '@/hooks/useRequest'

import EditDescBox from '@/components/form/editDescBox'
import Terminate, { RefProps } from '@/components/task/terminate'

import { getModelColumns } from '@/components/table/Columns'
import useListActions from '@/hooks/useListActions'
import Actions from '@/components/table/columns/Actions'

type Props = {
  pid: number
  name?: string
  query?: YParams.ResultListQuery
}
const ModelList: FC<Props> = ({ pid, name, query }) => {
  const [models, setModels] = useState<YStates.List<YModels.Model>>()
  const { data: remoteModels, run: getModels } = useRequest<YStates.List<YModels.Model>, [YParams.ModelsQuery]>('model/queryModels', {
    debounceWait: 100,
  })
  const [modelQuery, setQuery] = useState<YParams.ModelsQuery>({
    pid,
    ...(query || {}),
  })
  const [editingModel, setEditingModel] = useState<YModels.Model>()
  const terminateRef = useRef<RefProps>(null)

  useEffect(
    () =>
      query
        ? setQuery((q) => ({
            ...q,
            ...query,
          }))
        : setQuery({ pid }),
    [query],
  )

  useEffect(() => setModels(remoteModels), [remoteModels])

  useEffect(() => {
    const { name, startTime, state = -1 } = modelQuery
    if (name || startTime || state >= 0) {
      fetch()
    } else {
      setModels({ items: [], total: 0 })
    }
  }, [modelQuery])

  const tableChange: TableProps<YModels.Model>['onChange'] = ({ current, pageSize }, filters, sorters = {}) => {}

  const pageChange = (page: number, pageSize: number) => {
    const offset = (page - 1) * (modelQuery.limit || 10)
    setQuery((query) => ({
      ...query,
      offset,
      limit: pageSize,
    }))
  }

  function fetch() {
    getModels(modelQuery)
  }

  const stop = (model: YModels.Model) => {
    terminateRef?.current?.confirm(model)
  }

  const editDesc = (model: YModels.Model) => {
    setEditingModel(undefined)
    setTimeout(() => setEditingModel(model), 0)
  }

  const getActions = useListActions({
    stop,
    editDesc,
  })
  const columns = [...getModelColumns(), Actions(getActions)]

  return (
    <div>
      <Table
        dataSource={models?.items}
        onChange={tableChange}
        rowKey={(record) => record.id}
        rowClassName={(record, index) => (index % 2 === 0 ? '' : 'oddRow')}
        columns={columns}
        pagination={{
          showQuickJumper: true,
          showSizeChanger: true,
          current: (modelQuery?.offset || 0) / (modelQuery?.limit || 10) + 1,
          total: models?.total,
          pageSize: modelQuery?.limit,
          onChange: pageChange,
        }}
      />
      {editingModel ? <EditDescBox type="model" record={editingModel} handle={fetch} /> : null}
      <Terminate ref={terminateRef} ok={fetch} />
    </div>
  )
}

export default ModelList
