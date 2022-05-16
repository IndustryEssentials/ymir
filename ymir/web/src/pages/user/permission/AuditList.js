import { connect } from "dva"
import { message, Table } from 'antd'
import { useState, useEffect } from "react"

import t from "@/utils/t"
import { format } from '@/utils/date'
import { STATES } from '@/constants/user'
import Actions from "@/components/table/actions"
import { AddDelTwoIcon, AddTwoIcon, SuccessIcon } from "@/components/common/icons"
import s from '../permission.less'
import StateTag from "@/components/user/stateTag"

const initQuery = {
  limit: 20,
  offset: 0,
}

function AuditList({ getUsers, setUserState }) {

  const [users, setUsers] = useState([])
  const [total, setTotal] = useState(0)
  const [query, setQuery] = useState(initQuery)

  useEffect(() => {
    getUserList()
  }, [query])

  const columns = [
    {
      title: showTitle("user.column.name"),
      dataIndex: "username",
      ellipsis: true,
    },
    {
      title: showTitle("user.column.email"),
      dataIndex: "email",
    },
    {
      title: showTitle("user.column.apply_time"),
      dataIndex: "create_datetime",
      render: (datetime) => format(datetime),
      width: 200,
      align: 'center',
    },
    {
      title: showTitle("common.state"),
      dataIndex: "state",
      render: (state) => <StateTag state={state} />, 
    },
    {
      title: showTitle("common.action"),
      key: "action",
      dataIndex: "action",
      render: (text, record) => <Actions menus={actionMenus(record)} />,
      className: s.tab_actions,
      align: "center",
      width: "280px",
    },
  ]

  const actionMenus = (record) => {
    const { id, name, state, user_role } = record
    return [
      {
        key: "resolve",
        label: t("user.action.resolve"),
        onclick: () => resolve(id, name),
        hidden: () => [STATES.ACTIVE, STATES.DEACTIVED].indexOf(state) > -1,
        icon: <SuccessIcon />,
      },
      {
        key: "reject",
        label: t("user.action.reject"),
        onclick: () => reject(id, name),
        hidden: () => state !== STATES.REGISTERED,
        icon: <AddDelTwoIcon />,
      },
    ]
  }

  async function getUserList() {
    const result = await getUsers(query)
    if (result) {
      setUsers(result.items)
      setTotal(result.total)
    }
  }

  function pageChange({ current, pageSize }) {
    const limit = pageSize
    const offset = (current - 1) * pageSize
    setQuery({ limit, offset })
  }

  async function resolve(id, name) {
    const result = await setUserState({ id, state: STATES.ACTIVE })
    if (result) {
      message.success(t('user.audit.resolve.success'))
      getUserList()
    }
  }

  async function reject(id, name) {
    const result = await setUserState({ id, state: STATES.DECLINED })
    if (result) {
      message.success(t('user.audit.reject.success'))
      getUserList()
    }
  }

  function showTitle(str) {
    return <strong>{t(str)}</strong>
  }

  return (
    <Table
      dataSource={users}
      columns={columns}
      onChange={pageChange}
      rowKey={(record) => record.id}
      pagination={{
        showQuickJumper: true,
        showSizeChanger: true,
        total: total,
        defaultPageSize: query.limit,
        defaultCurrent: 1,
      }}
    ></Table>
  )
}

const props = (state) => {
  return {}
}

const actions = (dispatch) => {
  return {
    getUsers(payload) {
      return dispatch({
        type: 'user/getUsers',
        payload,
      })
    },
    setUserState(payload) {
      return dispatch({
        type: 'user/setUserState',
        payload,
      })
    }
  }
}

export default connect(props, actions)(AuditList)
