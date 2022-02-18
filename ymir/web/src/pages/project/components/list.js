
import React, { useEffect, useRef, useState } from "react"
import { connect } from 'dva'
import { useHistory } from "umi"
import { List, Skeleton, Space, Pagination, Col, Row, } from "antd"

import t from "@/utils/t"
import Del from './del'
import s from "./list.less"
import { EditIcon, DeleteIcon, AddIcon } from "@/components/common/icons"

const ProjectList = ({ role, filter, getProjects, list, query, updateQuery, resetQuery }) => {

  const history = useHistory()
  const [projects, setProjects] = useState([])
  const [total, setTotal] = useState(1)
  const delRef = useRef(null)

  /** use effect must put on the top */
  useEffect(() => {
    setProjects(list.items)
    setTotal(list.total)
  }, list)

  useEffect(() => {
    getData()
  }, [query])

  useEffect(() => {
    JSON.stringify(filter) !== JSON.stringify(query) && setQuery({ ...query, ...filter })
  }, [filter])

  const pageChange = ({ current, pageSize }) => {
    const limit = pageSize
    const offset = (current - 1) * pageSize
    setQuery((old) => ({ ...old, limit, offset }))
  }

  async function getData() {
    await getProjects(query)
  }

  const moreList = (record) => {
    const { id, name } = record

    const menus = [
      {
        key: "edit",
        label: t("project.action.edit"),
        onclick: () => history.push(`/home/project/add/${id}`),
        icon: <EditIcon />,
      },
      {
        key: "del",
        label: t("project.action.del"),
        onclick: () => del(id, name),
        icon: <DeleteIcon />,
      },
    ]

    return menus
  }

  const del = (id, name) => {
    delRef.current.del(id, name)
  }

  const delOk = (id) => {
    setProjects(projects.filter(project => project.id !== id))
    setTotal(old => old - 1)
    getData()
  }

  const more = (item) => {
    return (
      <Space>
        {moreList(item).filter(menu => !(menu.hidden && menu.hidden())).map((action) => (
          <a
            type='link'
            className={action.className}
            key={action.key}
            onClick={action.onclick}
            title={action.label}
          >
            {action.icon}
          </a>
        ))}
      </Space>
    )
  }

  const addBtn = (
    <div className={s.addBtn} onClick={() => history.push('/home/project/add')}><AddIcon />{t('project.new.label')}</div>
  )

  const renderItem = (item) => {
    const title = <Row wrap={false}>
      <Col flex={1}>{item.name}</Col>
      <Col>{more(item)}</Col>
    </Row>
    const desc = <>
      <Row>
        <Col className={s.content.stats}>Datasets</Col>
        <Col className={s.content.stats}>Models</Col>
        <Col className={s.content.stats}>训练集/测试集/挖掘集</Col>
        <Col className={s.content.stats}>迭代轮次</Col>
      </Row>
      <Row>
        <Col flex={1}>{t('project.content.desc')}: {item.desc}</Col>
        <Col>{item.createTime}</Col>
      </Row>
    </>

    return <List.Item className={item.state ? 'success' : 'failure'}>
      <Skeleton active loading={item.loading}>
        <List.Item.Meta title={title} description={desc}>
        </List.Item.Meta>
      </Skeleton>
    </List.Item>
  }

  return (
    <div className={s.projectContent}>
      {addBtn}
      <List
        className={s.list}
        dataSource={projects}
        renderItem={renderItem}
      />
      <Pagination className={s.pager} onChange={pageChange}
        defaultCurrent={1} defaultPageSize={query.limit} total={total}
        showTotal={() => t('project.list.total', { total })}
        showQuickJumper showSizeChanger />
      <Del ref={delRef} ok={delOk} />
    </div>
  )
}

const props = (state) => {
  return {
    list: state.project.list,
    query: state.project.query,
  }
}

const actions = (dispatch) => {
  return {
    getProjects: (payload) => {
      return dispatch({
        type: 'project/getProjects',
        payload,
      })
    },
    updateQuery: (query) => {
      return dispatch({
        type: 'project/updateQuery',
        payload: query,
      })
    },
    resetQuery: (        ) => {
      return dispatch({
        type: 'project/resetQuery',
      })
    },
  }
}

export default connect(props, actions)(ProjectList)
