import { connect } from "dva"
import { message, Table } from 'antd'
import { useState, useEffect } from "react"

import t from "@/utils/t"
import { format } from '@/utils/date'
import { ROLES, getRolesLabel } from '@/constants/user'
import { AddDelTwoIcon, AddTwoIcon, ShutIcon } from "@/components/common/icons"
import s from '../permission.less'
import Actions from "@/components/table/actions"
import confirm from '@/components/common/dangerConfirm'

const initQuery = {
  limit: 20,
  offset: 0,
}

function UserList({ getUsers, setUserRole, off }) {

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
      title: showTitle("user.column.role"),
      dataIndex: "role",
      render: (role) => t(getRolesLabel(role)),
    },
    {
      title: showTitle("user.column.email"),
      dataIndex: "email",
    },
    {
      title: showTitle("user.column.last"),
      key: "last_login_datetime",
      dataIndex: "last_login_datetime",
      render: (datetime) => datetime ? format(datetime) : null,
      width: 200,
      align: 'center',
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
    const { id, username, role } = record
    return [
      {
        key: "add",
        label: t("user.action.admin"),
        onclick: () => setAdmin(id),
        hidden: () => role !== ROLES.USER,
        icon: <AddTwoIcon />,
      },
      {
        key: "remove",
        label: t("user.action.user"),
        onclick: () => setUser(id),
        hidden: () => role !== ROLES.ADMIN,
        icon: <AddDelTwoIcon />,
      },
      {
        key: "off",
        label: t("user.action.off"),
        onclick: () => setOff(id, username),
        hidden: () => role === ROLES.SUPER,
        icon: <ShutIcon />,
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

  function setAdmin(id) {
    setRole(id, ROLES.ADMIN)
  }

  function setUser(id) {
    setRole(id, ROLES.USER, t('permission.role.user.succcess'))
  }

  async function setRole(id, role, msg = t('permission.role.admin.succcess')) {
    const result = await setUserRole(id, role)
    if (result) {
      message.success(msg)
      getUserList()
    }
  }

  function setOff(id, name) {
    confirm({
      content: t("permission.off.confirm", { name }),
      onOk: async () => {
        const result = await off(id)
        if (result) {
          message.success(t('permission.off.succcess'))
          getUserList()
        }
      },
      okText: t('user.action.off'),
    })

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
        // showTotal: (total) => t("model.pager.total.label", { total }),
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
        type: 'user/getActiveUsers',
        payload,
      })
    },
    setUserRole(id, role) {
      return dispatch({
        type: 'user/setUserRole',
        payload: { id, role },
      })
    },
    off(id) {
      return dispatch({
        type: 'user/off',
        payload: id,
      })
    },
  }
}
export default connect(props, actions)(UserList)
