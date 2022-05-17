import React, { useEffect, useState } from "react"
import { connect } from 'dva'
import s from "../index.less"
import { Table, Space, Button, message, } from "antd"

import t from "@/utils/t"
import { humanize } from "@/utils/number"
import Actions from "@/components/table/actions"
import { EyeOnIcon } from "@/components/common/icons"
import useRestore from "@/hooks/useRestore"

const HiddenList = ({ module, pid, ...func }) => {
  const [list, setHiddenList] = useState([])
  const [total, setTotal] = useState(0)
  const [query, setQuery] = useState(null)
  const [selected, setSelected] = useState([])
  const restoreAction = useRestore(pid)

  useEffect(() => {
    // initial query
    setQuery({})
    setSelected([])
  }, [module])

  useEffect(() => {
    query && fetch()
  }, [query])

  const columns = [
    {
      title: showTitle("dataset.column.name"),
      dataIndex: "name",
      render: (name, { versionName }) => `${name} ${versionName}`,
      ellipsis: { showTitle: true },
    },
    {
      title: showTitle("dataset.column.asset_count"),
      dataIndex: "assetCount",
      render: (num) => humanize(num),
    },
    {
      title: showTitle("dataset.column.hidden_time"),
      dataIndex: "updateTime",
      sorter: true,
      sortDirections: ['descend', 'ascend'],
      defaultSortOrder: 'descend',
    },
    {
      title: showTitle("dataset.column.action"),
      dataIndex: "id",
      render: (id, record) => <Actions menus={actionMenus(record)} />,
      align: "center",
    },
  ]

  const actionMenus = ({ id }) => [{
    key: "restore",
    label: t("common.action.restore"),
    onclick: () => restore([id]),
    icon: <EyeOnIcon />,
  }]

  async function fetch() {
    const result = await func.getHiddenList(module, pid, query)
    if (result) {
      const { items, total } = result
      if (query.offset && total <= query.offset) {
        return setQuery(old => ({ ...old, offset: query.offset - query.limit }))
      }
      setHiddenList(items)
      setTotal(total)
    }
  }

  async function restore(ids = []) {
    const result = await restoreAction(module, ids)
    if (result) {
      // refresh list
      fetch()
      // init selected
      setSelected([])
    }
  }

  function multipleRestore() {
    restore(selected)
  }

  function showTitle(str) {
    return <strong>{t(str)}</strong>
  }

  function pageChange({ current, pageSize }, filters, sorters) {
    const is_desc = sorters.order !== 'ascend'
    const sortColumn = sorters.field === 'updateTime' ? 'update_datetime' : undefined
    const limit = pageSize
    const offset = (current - 1) * pageSize
    setQuery(old => ({
      ...old,
      limit,
      offset,
      order_by: sorters.column ? sortColumn : 'id',
      is_desc
    }))
  }

  function rowSelectChange(keys) {
    setSelected(keys)
  }

  return <div className={s.hiddenList}>
    <Space className='actions'>
      <Button disabled={!selected.length} type="primary" onClick={multipleRestore}>
        <EyeOnIcon /> {t("common.action.multiple.restore")}
      </Button>
    </Space>
    <div className={`list ${s.table}`}>
      <Table
        dataSource={list}
        pagination={{
          total,
          showQuickJumper: true,
          showSizeChanger: true,
          defaultCurrent: 1,
          defaultPageSize: query?.offset || 10,
        }}
        onChange={pageChange}
        rowKey={(record) => record.id}
        rowSelection={{
          selectedRowKeys: selected,
          onChange: (keys) => rowSelectChange(keys),
        }}
        rowClassName={(record, index) => index % 2 === 0 ? '' : 'oddRow'}
        columns={columns}
      ></Table>
    </div>
  </div>
}

const props = (state) => {
  return {
    logined: state.user.logined,
  }
}

const actions = (dispatch) => {
  return {
    getHiddenList(module, id, query) {
      const type = `${module}/getHiddenList`
      return dispatch({
        type,
        payload: { ...query, project_id: id, },
      })
    },
  }
}

export default connect(props, actions)(HiddenList)
