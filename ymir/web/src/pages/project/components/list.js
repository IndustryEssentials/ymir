
import React, { useEffect, useRef, useState } from "react"
import { connect } from 'dva'
import { useHistory, Link } from "umi"
import { List, Skeleton, Space, Pagination, Col, Row, Card, Button, Form, Input, } from "antd"

import t from "@/utils/t"
import { getStageLabel } from '@/constants/project'
import Del from './del'
import s from "./list.less"
import { EditIcon, DeleteIcon, AddIcon, SearchIcon } from "@/components/common/icons"

const ProjectList = ({ getProjects, list, query, updateQuery, resetQuery }) => {

  const history = useHistory()
  const [projects, setProjects] = useState([])
  const [total, setTotal] = useState(1)
  const [form] = Form.useForm()
  const delRef = useRef(null)

  /** use effect must put on the top */
  useEffect(() => {
    setProjects(list.items)
    setTotal(list.total)
  }, [list])

  useEffect(() => {
    getData()
  }, [query])

  const pageChange = (current, pageSize) => {
    const limit = pageSize
    const offset = (current - 1) * pageSize
    updateQuery({ ...query, limit, offset })
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

  const search = (values) => {
    updateQuery({ ...query, ...values })
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
    <Button className={s.addBtn} type="primary" onClick={() => history.push('/home/project/add')} icon={<AddIcon />}>{t('project.new.label')}</Button>
  )

  const searchPanel = (
    <Form
      name='queryForm'
      form={form}
      layout="inline"
      onValuesChange={search}
      colon={false}
    >
      <Form.Item name="name" label={t('project.query.name')}>
        <Input style={{ width: '230%' }} placeholder={t("project.query.name.placeholder")} allowClear suffix={<SearchIcon />} />
      </Form.Item>
    </Form>
  )

  const renderItem = (item) => {
    const title = <Row wrap={false} className={s.title}>
      <Col flex={1}>
        <Space>
          <span className={s.name}><Link to={`/home/project/detail/${item.id}`}>{item.name}</Link></span>
          <span className={s.titleItem}>
            <span className={s.titleLabel}>{t('project.train_classes')}:</span>
            <span className={s.titleContent}>{item.keywords.join(',')}</span>
          </span>
          <span className={s.titleItem}>
            <span className={s.titleLabel}>{t('project.target.map')}:</span>
            <span className={s.titleContent}>{item?.targetMap}</span>
          </span>
          <span className={s.titleItem}>
            <span className={s.titleLabel}>{t('project.iteration.current')}:</span>
            <span className={s.titleContent}>{t(getStageLabel(item.currentStage, item.round))}</span>
          </span>
        </Space>
      </Col>
      <Col>{more(item)}</Col>
    </Row>
    const desc = <>
      <Row className={s.content} justify="center">
        <Col span={4} className={s.stats}>
          <div className={s.contentLabel}>Datasets</div>
          <div className={s.contentContent}>{item.setCount}</div>
        </Col>
        <Col span={4} className={s.stats}>
          <div className={s.contentLabel}>Models</div>
          <div className={s.contentContent}>{item.modelCount}</div>
        </Col>
        <Col span={12} className={s.stats}>
          <div className={s.contentLabel}>{t('project.train_set')}/{t('project.test_set')}/{t('project.mining_set')}</div>
          <div className={s.sets} title={`${t('project.train_set')}:${item.trainSet?.name}\n${t('project.test_set')}:${item.testSet?.name}\n${t('project.mining_set')}:${item.miningSet?.name}`}>{item.trainSet?.name}/{item.testSet?.name}/{item.miningSet?.name}</div>
        </Col>
        <Col span={4} className={s.stats}>
          <div className={s.contentLabel}>{t('project.iteration.number')}</div>
          <div className={s.contentContent}>{item.round}/{item?.targetIteration}</div>
        </Col>
      </Row>
      <Row>
        <Col flex={1}><span className={s.bottomLabel}>{t('project.content.desc')}:</span> <span className={s.bottomContent}>{item.description}</span></Col>
        <Col><span className={s.bottomContent}>{item.createTime}</span></Col>
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
      <Space className={s.actions}>{addBtn}</Space>
      <Card>
        {searchPanel}
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
      </Card>
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
    resetQuery: () => {
      return dispatch({
        type: 'project/resetQuery',
      })
    },
  }
}

export default connect(props, actions)(ProjectList)
