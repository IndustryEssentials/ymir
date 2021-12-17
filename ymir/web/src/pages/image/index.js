import React, { useEffect, useRef, useState } from "react"
import { connect } from 'dva'
import styles from "./index.less"
import { Link, useHistory, useParams } from "umi"
import { Form, List, Input, Menu, Modal, Radio, Card, Skeleton, Space, Button, Pagination, Col, Row, } from "antd"

import t from "@/utils/t"
import { getImageTypes } from '@/constants/query'
import Breadcrumbs from "@/components/common/breadcrumb"
import { ImportIcon, ShieldIcon, VectorIcon, TipsIcon, More1Icon, TreeIcon, EditIcon, DeleteIcon, FileDownloadIcon, AddIcon, SearchIcon, MoreIcon, UserSettingsIcon, ShareIcon, LinkIcon } from "../../components/common/icons"

const { confirm } = Modal
const { useForm } = Form

const tabsTitle = [
  { tab: t('image.tab.my.title'), key: 'my', },
  { tab: t('image.tab.public.title'), key: 'public', },
]

const initQuery = {
  name: "",
  type: "",
  offset: 0,
  limit: 20,
}

function Image({ getImages, delImage, updateImage }) {
  const { keyword } = useParams()
  const history = useHistory()
  const [images, setImages] = useState([])
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

  const types = getImageTypes()


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
    // const result = await getImages(params)
    // mock data
    const result = {
      items: [
        { id: 0, name: 'image 0', type: 1, remote: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 0, },
        { id: 1, name: 'image 1', type: 1, remote: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 1, },
        { id: 2, name: 'image 2', type: 2, remote: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 1, },
        { id: 3, name: 'image 3', type: 2, remote: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 1, },
        { id: 4, name: 'image 4', type: 2, remote: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 2, },
        { id: 5, name: 'image 5', type: 2, remote: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 3, },
        { id: 6, name: 'image 6', type: 1, remote: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 4, },
        { id: 7, name: 'image 7', type: 2, remote: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 0, },
        { id: 8, name: 'image 8', type: 1, remote: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 0, },
        { id: 9, name: 'image 9', type: 1, remote: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 0, },
        { id: 10, name: 'image 10', type: 2, remote: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 3, },
        { id: 11, name: 'image 11', type: 1, remote: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 3, },
        { id: 12, name: 'image 12', type: 1, remote: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 3, },
        { id: 13, name: 'image 13', type: 2, remote: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 3, },
        { id: 14, name: 'image 14', type: 1, remote: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 3, },
        { id: 15, name: 'image 15', type: 1, remote: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 3, },
        { id: 16, name: 'image 16', type: 1, remote: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 3, },
        { id: 17, name: 'image 17', type: 1, remote: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 3, },
        { id: 18, name: 'image 18', type: 1, remote: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 3, },
        { id: 19, name: 'image 19', type: 1, remote: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 3, },
      ],
      total: 56,
    }
    if (result) {
      const { items, total } = result
      setImages(() => items)
      setTotal(total)
    }
  }

  const moreList = (record) => {
    const { id, name, type, remote } = record
    return [
      {
        key: "link",
        label: t("image.action.link"),
        onclick: () => history.push(`/home/image/detail/${id}`),
        icon: <LinkIcon />,
      },
      {
        key: "share",
        label: t("image.action.share"),
        onclick: () => history.push('/home/image/share'),
        icon: <ShareIcon />,
      },
      {
        key: "edit",
        label: t("image.action.edit"),
        onclick: () => history.push(`/home/image/detail/${id}`),
        icon: <EditIcon />,
      },
      {
        key: "del",
        label: t("image.action.del"),
        onclick: () => del(id, name),
        className: styles.action_del,
        icon: <DeleteIcon />,
      },
      {
        key: "detail",
        label: t("image.action.detail"),
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
        const result = await delImage(id)
        if (result) {
          setImages(images.filter((model) => model.id !== id))
          setTotal(old => old - 1)
          getData()
        }
      },
      okText: t('task.action.del'),
      okButtonProps: { style: { backgroundColor: 'rgb(242, 99, 123)', borderColor: 'rgb(242, 99, 123)', } }
    })
  }


  const saveName = async (record, name) => {
    const result = await updateImage(record.id, name)
    if (result) {
      setImages((images) =>
        images.map((model) => {
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
    <div className={styles.addBtn}><AddIcon />{t('image.new.label')}</div>
  )

  const renderItem = (item) => {
    const title = <Row wrap={false}>
      <Col flex={1}>{item.name}</Col>
      <Col>{more(item)}</Col>
    </Row>
    const desc = <Row><Col className={styles.desc} flex={1}>
      <Space className={styles.info}>
        <span className={styles.infoItem}><span className={styles.infoLabel}>{t('image.list.item.type')}</span>{item.type}</span>
        <span className={styles.infoItem}><span className={styles.infoLabel}>{t('image.list.item.remote')}</span>{item.remote}</span>
        <span className={styles.infoItem}><span className={styles.infoLabel}>{t('image.list.item.desc')}</span>{item.desc}</span>
      </Space>
      <div className={styles.related}>{t('image.list.item.related')}{item.relative.join(',')}</div>
    </Col>
      <Col><Button key='train' onClick={() => history.push(`/home/task/train?image=${item.id}`)}>{t('image.list.train.btn')}</Button></Col>
    </Row>
    return <List.Item className={item.state ? 'success' : 'failure'}>
      <Skeleton active loading={item.loading}>
        <List.Item.Meta title={title} description={desc}>
        </List.Item.Meta>
      </Skeleton>
    </List.Item>
  }

  const myImage = (
    <div className={styles.my}>
      {addBtn}
      <List
        className={styles.list}
        dataSource={images}
        renderItem={renderItem}
      />
      <Pagination onChange={() => getData()} defaultCurrent={1} defaultPageSize={query.limit} total={total} showQuickJumper showSizeChanger></Pagination>
    </div>
  )

  const publicImage = ('')

  const contents = {
    my: myImage,
    public: publicImage,
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
        label={t("image.column.type")}
      >
        <Radio.Group options={types} optionType="button"></Radio.Group>
      </Form.Item>
      <Form.Item name="name" label={t('model.query.name')}>
        <Input placeholder={t("model.query.name.placeholder")} allowClear suffix={<SearchIcon />} />
      </Form.Item>
    </Form>
  )

  return (
    <div className={styles.image}>
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
    getImages: (payload) => {
      return dispatch({
        type: 'image/getImages',
        payload,
      })
    },
    delImage: (payload) => {
      return dispatch({
        type: 'image/delImage',
        payload,
      })
    },
    updateImage: (id, name) => {
      return dispatch({
        type: 'image/updateImage',
        payload: { id, name },
      })
    },
  }
}

export default connect(props, actions)(Image)
