
import React, { useEffect, useRef, useState } from "react"
import { connect } from 'dva'
import { Link, useHistory, useParams } from "umi"
import { Form, List, Input, Menu, Modal, Radio, Card, Skeleton, Space, Button, Pagination, Col, Row, } from "antd"

import t from "@/utils/t"
import { ROLES } from '@/constants/user'
import { TYPES, STATES } from '@/constants/image'
import s from "./list.less"
import { VectorIcon, TrainIcon, TipsIcon, EditIcon, DeleteIcon, AddIcon, MoreIcon, ShareIcon, LinkIcon } from "@/components/common/icons"

const { confirm } = Modal

const initQuery = {
  name: "",
  type: "",
  offset: 0,
  limit: 20,
}

const ImageList = ({ role, filter, getImages, delImage, updateImage }) => {

  const history = useHistory()
  const [images, setImages] = useState([])
  const [total, setTotal] = useState(1)
  const [query, setQuery] = useState(initQuery)

  /** use effect must put on the top */
  useEffect(() => {
    getData()
  }, [query])

  useEffect(() => {
    filter && setQuery({ ...query, ...filter })
  }, [filter])

  const pageChange = ({ current, pageSize }) => {
    const limit = pageSize
    const offset = (current - 1) * pageSize
    setQuery((old) => ({ ...old, limit, offset }))
  }

  async function getData() {
    let params = {
      ...query,
    }

    // const result = await getImages(params)
    // mock data
    const result = {
      items: [
        { id: 0, name: 'image 0', type: 1, url: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 0, },
        { id: 1, name: 'image 1', type: 1, url: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 1, },
        { id: 2, name: 'image 2', type: 2, url: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 1, },
        { id: 3, name: 'image 3', type: 2, url: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 1, },
        { id: 4, name: 'image 4', type: 2, url: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 2, },
        { id: 5, name: 'image 5', type: 2, url: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 3, },
        { id: 6, name: 'image 6', type: 1, url: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 4, },
        { id: 7, name: 'image 7', type: 2, url: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 0, },
        { id: 8, name: 'image 8', type: 1, url: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 0, },
        { id: 9, name: 'image 9', type: 1, url: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 0, },
        { id: 10, name: 'image 10', type: 2, url: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 3, },
        { id: 11, name: 'image 11', type: 1, url: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 3, },
        { id: 12, name: 'image 12', type: 1, url: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 3, },
        { id: 13, name: 'image 13', type: 2, url: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 3, },
        { id: 14, name: 'image 14', type: 1, url: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 3, },
        { id: 15, name: 'image 15', type: 1, url: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 3, },
        { id: 16, name: 'image 16', type: 1, url: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 3, },
        { id: 17, name: 'image 17', type: 1, url: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 3, },
        { id: 18, name: 'image 18', type: 1, url: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 3, },
        { id: 19, name: 'image 19', type: 1, url: 'docker hub name', desc: 'image desc', relative: [2, 3, 4, 5], state: 3, },
      ],
      total: 56,
    }
    console.log('get data result: ', result)
    if (result) {
      const { items, total } = result
      setImages(() => items)
      setTotal(total)
    }
  }

  const moreList = (record) => {
    const { id, name, state, type, url, links } = record

    const menus = [
      {
        key: "link",
        label: t("image.action.link"),
        onclick: () => link(id, name, links),
        hidden: () => !isTrain(type) || !isDone(state),
        icon: <LinkIcon />,
      },
      {
        key: "share",
        label: t("image.action.share"),
        onclick: () => share(id, name),
        hidden: () => !isDone(),
        icon: <ShareIcon />,
      },
      {
        key: "edit",
        label: t("image.action.edit"),
        onclick: () => history.push(`/home/image/add/${id}`),
        icon: <EditIcon />,
      },
      {
        key: "del",
        label: t("image.action.del"),
        onclick: () => del(id, name),
        icon: <DeleteIcon />,
      },
    ]

    const detail = {
      key: "detail",
      label: t("image.action.detail"),
      onclick: () => history.push(`/home/model/verify/${id}`),
      icon: <MoreIcon />,
    }
    return isAdmin() ? [...menus, detail] : [detail]
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

  const share = (id, name) => {
    // todo , open a modal for entering share info.
  }

  const links = (id, name, links) => {
    // todo , open a modal for linking
  }

  function isAdmin() {
    return role > ROLES.USER
  }

  function isTrain(type) {
    return type === TYPES.TRAINING
  }

  function isDone (state) {
    return state === STATES.DONE
  }

  const more = (item) => {
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
    <div className={s.addBtn} onClick={() => history.push('/home/image/add')}><AddIcon />{t('image.new.label')}</div>
  )

  const renderItem = (item) => {
    const title = <Row wrap={false}>
      <Col flex={1}>{item.name}</Col>
      <Col>{more(item)}</Col>
    </Row>
    const type = isTrain(item.type) ? 'train' : 'mining'
    const desc = <Row><Col className={s.desc} flex={1}>
      <Space className={s.info}>
        <span className={s.infoItem}><span className={s.infoLabel}>{t('image.list.item.type')}</span>{item.type}</span>
        <span className={s.infoItem}><span className={s.infoLabel}>{t('image.list.item.url')}</span>{item.url}</span>
        <span className={s.infoItem}><span className={s.infoLabel}>{t('image.list.item.desc')}</span>{item.desc}</span>
      </Space>
      <div className={s.related}>{t('image.list.item.related')}{item.relative.join(',')}</div>
    </Col>
      <Col>
        <Button key={type} onClick={() => history.push(`/home/task/${type}?image=${item.id}`)}>
          {isTrain(item.type) ? <TrainIcon /> : <VectorIcon />} {t(`image.list.${type}.btn`)}
        </Button>
      </Col>
    </Row>

    return <List.Item className={item.state ? 'success' : 'failure'}>
      <Skeleton active loading={item.loading}>
        <List.Item.Meta title={title} description={desc}>
        </List.Item.Meta>
      </Skeleton>
    </List.Item>
  }

  return (
    <div className={s.imageContent}>
      {addBtn}
      <List
        className={s.list}
        dataSource={images}
        renderItem={renderItem}
      />
      <Pagination className={s.pager} onChange={pageChange}
        defaultCurrent={1} defaultPageSize={query.limit} total={total}
        showQuickJumper showSizeChanger />
    </div>
  )
}


const props = (state) => {
  return {
    role: state.user.role,
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

export default connect(props, actions)(ImageList)
