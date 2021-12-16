import React, { useEffect, useRef, useState } from "react"
import { connect } from 'dva'
import styles from "./index.less"
import { Link, useHistory, useParams } from "umi"
import { Form, List, Input, Menu, Modal, Radio, Card, Skeleton, Space, Button, Pagination, Col, Row, } from "antd"

import t from "@/utils/t"
import { getMirrorTypes } from '@/constants/query'
import Breadcrumbs from "@/components/common/breadcrumb"
import { ImportIcon, ShieldIcon, VectorIcon, TipsIcon, More1Icon, TreeIcon, EditIcon, DeleteIcon, FileDownloadIcon, AddIcon, SearchIcon, MoreIcon, UserSettingsIcon, ShareIcon, LinkIcon } from "../../components/common/icons"

const { confirm } = Modal
const { useForm } = Form

const tabsTitle = [
  { tab: t('mirror.tab.my.title'), key: 'my', },
  { tab: t('mirror.tab.public.title'), key: 'public', },
]

const initQuery = {
  name: "",
  type: "",
  offset: 0,
  limit: 20,
}

function Mirror({ getMirrors, delMirror, updateMirror }) {
  const { keyword } = useParams()
  const history = useHistory()
  const [mirrors, setMirrors] = useState([])
  const [total, setTotal] = useState(0)
  const [form] = useForm()
  const [active, setActive] = useState(tabsTitle[0].key)
  const [query, setQuery] = useState(initQuery)

  /** use effect must put on the top */
  useEffect(() => {
    getData()
  }, [query])

  useEffect(() => {
    if (keyword) {
      setQuery(old => ({ ...old, name: keyword }))
      form.setFieldsValue({ name: keyword })
    }
  }, [keyword])

  const types = getMirrorTypes()


  const pageChange = ({ current, pageSize }) => {
    const limit = pageSize
    const offset = (current - 1) * pageSize
    setQuery((old) => ({ ...old, limit, offset }))
  }

  async function getData() {
    let params = {
      offset: query.offset,
      limit: query.limit,
      type: query.type,
    }
    if (query.name) {
      params.name = query.name
    }
    // const result = await getMirrors(params)
    // mock data
    const result = {
      items: [
        { id: 0, name: 'mirror 0', type: 1, remote: 'docker hub name', desc: 'mirror desc', relative: [2, 3, 4, 5], state: 0, },
        { id: 1, name: 'mirror 1', type: 1, remote: 'docker hub name', desc: 'mirror desc', relative: [2, 3, 4, 5], state: 1, },
        { id: 2, name: 'mirror 2', type: 2, remote: 'docker hub name', desc: 'mirror desc', relative: [2, 3, 4, 5], state: 1, },
        { id: 3, name: 'mirror 3', type: 2, remote: 'docker hub name', desc: 'mirror desc', relative: [2, 3, 4, 5], state: 1, },
        { id: 4, name: 'mirror 4', type: 2, remote: 'docker hub name', desc: 'mirror desc', relative: [2, 3, 4, 5], state: 2, },
        { id: 5, name: 'mirror 5', type: 2, remote: 'docker hub name', desc: 'mirror desc', relative: [2, 3, 4, 5], state: 3, },
        { id: 6, name: 'mirror 6', type: 1, remote: 'docker hub name', desc: 'mirror desc', relative: [2, 3, 4, 5], state: 4, },
        { id: 7, name: 'mirror 7', type: 2, remote: 'docker hub name', desc: 'mirror desc', relative: [2, 3, 4, 5], state: 0, },
        { id: 8, name: 'mirror 8', type: 1, remote: 'docker hub name', desc: 'mirror desc', relative: [2, 3, 4, 5], state: 0, },
        { id: 9, name: 'mirror 9', type: 1, remote: 'docker hub name', desc: 'mirror desc', relative: [2, 3, 4, 5], state: 0, },
        { id: 10, name: 'mirror 10', type: 2, remote: 'docker hub name', desc: 'mirror desc', relative: [2, 3, 4, 5], state: 3, },
        { id: 11, name: 'mirror 11', type: 1, remote: 'docker hub name', desc: 'mirror desc', relative: [2, 3, 4, 5], state: 3, },
        { id: 12, name: 'mirror 12', type: 1, remote: 'docker hub name', desc: 'mirror desc', relative: [2, 3, 4, 5], state: 3, },
        { id: 13, name: 'mirror 13', type: 2, remote: 'docker hub name', desc: 'mirror desc', relative: [2, 3, 4, 5], state: 3, },
        { id: 14, name: 'mirror 14', type: 1, remote: 'docker hub name', desc: 'mirror desc', relative: [2, 3, 4, 5], state: 3, },
        { id: 15, name: 'mirror 15', type: 1, remote: 'docker hub name', desc: 'mirror desc', relative: [2, 3, 4, 5], state: 3, },
        { id: 16, name: 'mirror 16', type: 1, remote: 'docker hub name', desc: 'mirror desc', relative: [2, 3, 4, 5], state: 3, },
        { id: 17, name: 'mirror 17', type: 1, remote: 'docker hub name', desc: 'mirror desc', relative: [2, 3, 4, 5], state: 3, },
        { id: 18, name: 'mirror 18', type: 1, remote: 'docker hub name', desc: 'mirror desc', relative: [2, 3, 4, 5], state: 3, },
        { id: 19, name: 'mirror 19', type: 1, remote: 'docker hub name', desc: 'mirror desc', relative: [2, 3, 4, 5], state: 3, },
      ],
      total: 56,
    }
    if (result) {
      const { items, total } = result
      setMirrors(() => items)
      setTotal(total)
    }
  }

  const moreList = (record) => {
    const { id, name, type, remote } = record
    return [
      {
        key: "link",
        label: t("mirror.action.link"),
        onclick: () => history.push(`/home/mirror/detail/${id}`),
        icon: <LinkIcon />,
      },
      {
        key: "share",
        label: t("mirror.action.share"),
        onclick: () => history.push('/home/mirror/share'),
        icon: <ShareIcon />,
      },
      {
        key: "edit",
        label: t("mirror.action.edit"),
        onclick: () => history.push(`/home/mirror/detail/${id}`),
        icon: <EditIcon />,
      },
      {
        key: "del",
        label: t("mirror.action.del"),
        onclick: () => del(id, name),
        className: styles.action_del,
        icon: <DeleteIcon />,
      },
      {
        key: "detail",
        label: t("mirror.action.detail"),
        onclick: () => history.push(`/home/model/verify/${id}`),
        icon: <MoreIcon />,
      },
    ]
  }

  const edit = (record) => {
    setCurrent({})
    setTimeout(() => setCurrent(record), 0)
  }

  const del = (id, name) => {
    confirm({
      icon: <TipsIcon style={{ color: 'rgb(242, 99, 123)' }} />,
      content: t("model.action.del.confirm.content", { name }),
      onOk: async () => {
        const result = await delMirror(id)
        if (result) {
          setMirrors(mirrors.filter((model) => model.id !== id))
          setTotal(old => old - 1)
          getData()
        }
      },
      okText: t('task.action.del'),
      okButtonProps: { style: { backgroundColor: 'rgb(242, 99, 123)', borderColor: 'rgb(242, 99, 123)', } }
    })
  }


  const saveName = async (record, name) => {
    const result = await updateMirror(record.id, name)
    if (result) {
      setMirrors((mirrors) =>
        mirrors.map((model) => {
          if (model.id === record.id) {
            model.name = name
          }
          return model
        })
      )
    }
  }

  const add = () => {
    setSowAdd(true)
  }

  const search = (values) => {
    const name = values.name
    if (typeof name === 'undefined') {
      setQuery((old) => ({
        ...old,
        ...values,
        offset: initQuery.offset,
      }))
    } else {
      setTimeout(() => {
        if (name === form.getFieldValue('name')) {
          setQuery((old) => ({
            ...old,
            name,
            offset: initQuery.offset,
          }))
        }
      }, 1000)
    }
  }

  const resetQuery = () => {
    setQuery(initQuery)
    form.resetFields()
  }

  const more = (item) => {
    console.log('item: ', item, moreList(item))
    return (
      <Space>
        {moreList(item).map((action) => (
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
    <div className={styles.addBtn}><AddIcon />{t('mirror.new.label')}</div>
  )

  const renderItem = (item) => {
    const title = <Row wrap={false}>
      <Col flex={1}>{item.name}</Col>
      <Col>{more(item)}</Col>
    </Row>
    const desc = <Row><Col className={styles.desc} flex={1}>
      <Space className={styles.info}>
        <span className={styles.infoItem}><span className={styles.infoLabel}>{t('mirror.list.item.type')}</span>{item.type}</span>
        <span className={styles.infoItem}><span className={styles.infoLabel}>{t('mirror.list.item.remote')}</span>{item.remote}</span>
        <span className={styles.infoItem}><span className={styles.infoLabel}>{t('mirror.list.item.desc')}</span>{item.desc}</span>
      </Space>
      <div className={styles.related}>{t('mirror.list.item.related')}{item.relative.join(',')}</div>
    </Col>
      <Col><Button key='train' onClick={() => history.push(`/home/task/train?mirror=${item.id}`)}>{t('mirror.list.train.btn')}</Button></Col>
    </Row>
    return <List.Item className={item.state ? 'success' : 'failure'}>
      <Skeleton active loading={item.loading}>
        <List.Item.Meta title={title} description={desc}>
        </List.Item.Meta>
      </Skeleton>
    </List.Item>
  }

  const myMirror = (
    <div className={styles.my}>
      {addBtn}
      <List
        className={styles.list}
        dataSource={mirrors}
        renderItem={renderItem}
      />
      <Pagination onChange={() => getData()} defaultCurrent={1} defaultPageSize={query.limit} total={total} showQuickJumper showSizeChanger></Pagination>
    </div>
  )

  const publicMirror = ('')

  const contents = {
    my: myMirror,
    public: publicMirror,
  }

  const searchPanel = (
    <Form
      name='queryForm'
      form={form}
      layout="inline"
      initialValues={{ name: keyword || "" }}
      onValuesChange={search}
      size='large'
      colon={false}
    >
      <Form.Item
        name="type"
        label={t("mirror.column.type")}
      >
        <Radio.Group options={types} optionType="button"></Radio.Group>
      </Form.Item>
      <Form.Item name="name" label={t('model.query.name')}>
        <Input placeholder={t("model.query.name.placeholder")} allowClear suffix={<SearchIcon />} />
      </Form.Item>
    </Form>
  )

  return (
    <div className={styles.mirror}>
      <Breadcrumbs />
      <Card tabList={tabsTitle} activeTabKey={active} onTabChange={(key) => setActive(key)} tabBarExtraContent={searchPanel}>
        {contents[active]}
      </Card>
    </div>
  )
}

const props = (state) => {
  return {
    logined: state.user.logined,
  }
}

const actions = (dispatch) => {
  return {
    getMirrors: (payload) => {
      return dispatch({
        type: 'mirror/getMirrors',
        payload,
      })
    },
    delMirror: (payload) => {
      return dispatch({
        type: 'mirror/delMirror',
        payload,
      })
    },
    updateMirror: (id, name) => {
      return dispatch({
        type: 'mirror/updateMirror',
        payload: { id, name },
      })
    },
  }
}

export default connect(props, actions)(Mirror)
