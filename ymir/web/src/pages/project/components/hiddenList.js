import React, { useEffect, useState } from "react"
import { connect } from 'dva'
import s from "../index.less"
import { Table, Space, Button, message, } from "antd"

import t from "@/utils/t"
import { humanize } from "@/utils/number"
import Actions from "@/components/table/actions"
import { EyeOnIcon } from "@/components/common/icons"

const HiddenList = ({ module, pid, ...func }) => {
  const [list, setHiddenList] = useState([])
  const [total, setTotal] = useState(0)
  const [query, setQuery] = useState({})
  const [selected, setSelected] = useState([])

  useEffect(() => {
    if (pid) {
      fetch()
    }
  }, [pid])

  useEffect(() => {
    // initial query
    setQuery({})
    setSelected([])
  }, [module])

  useEffect(() => {
    fetch()
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
      setHiddenList(items)
      setTotal(total)
    }
  }

  async function restore(ids = []) {
    if (!ids.length) {
      return message.warn(t('common.selected.required'))
    }
    const result = await func.restore(module, pid, ids)
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

  function pageChange({ current, pageSize }) {
    const limit = pageSize
    const offset = (current - 1) * pageSize
    setQuery(old => ({
      ...old,
      limit,
      offset,
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
          defaultPageSize: query.offset || 10,
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
    restore(module, pid, ids) {
      const type = `${module}/restore`
      return dispatch({
        type,
        payload: { pid, ids, }
      })
    },
  }
}

export default connect(props, actions)(HiddenList)
