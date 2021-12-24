
import React, { useEffect, useRef, useState } from "react"
import { connect } from 'dva'
import { useHistory } from "umi"
import { List, Skeleton, Space, Button, Pagination, Col, Row, } from "antd"

import t from "@/utils/t"
import { ROLES } from '@/constants/user'
import { TYPES, STATES, getImageTypeLabel } from '@/constants/image'
import ShareModal from "./share"
import RelateModal from './relate'
import Del from './del'
import s from "./list.less"
import { VectorIcon, TrainIcon, TipsIcon, EditIcon, DeleteIcon, AddIcon, MoreIcon, ShareIcon, LinkIcon } from "@/components/common/icons"
import ImagesLink from "./imagesLink"

const initQuery = {
  name: undefined,
  type: undefined,
  offset: 0,
  limit: 20,
}

const ImageList = ({ role, filter, getImages }) => {

  const history = useHistory()
  const [images, setImages] = useState([])
  const [total, setTotal] = useState(1)
  const [query, setQuery] = useState(initQuery)
  const shareModalRef = useRef(null)
  const linkModalRef = useRef(null)
  const delRef = useRef(null)

  /** use effect must put on the top */
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
    let params = {
      ...query,
    }

    const result = await getImages(params)
    if (result) {
      const { items, total } = result
      setImages(() => items)
      setTotal(total)
    }
  }

  const moreList = (record) => {
    const { id, name, state, type, url, related, is_shared } = record

    const menus = [
      {
        key: "link",
        label: t("image.action.link"),
        onclick: () => link(id, name, related),
        hidden: () => (!isTrain(type) || !isDone(state)),
        icon: <LinkIcon />,
      },
      {
        key: "share",
        label: t("image.action.share"),
        onclick: () => share(id, name),
        hidden: () => !isDone(state) || is_shared,
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
      onclick: () => history.push(`/home/image/detail/${id}`),
      icon: <MoreIcon />,
    }
    return isAdmin() ? [...menus, detail] : [detail]
  }

  const edit = (record) => {
    setCurrent({})
    setTimeout(() => setCurrent(record), 0)
  }

  const del = (id, name) => {
    delRef.current.del(id, name)
  }

  const delOk = (id) => {
    setImages(images.filter(image => image.id !== id))
    setTotal(old => old - 1)
    getData()
  }

  const relateOk = () => {
    getData()
  }

  const share = (id, name) => {
    shareModalRef.current.show(id, name)
  }

  const link = (id, name, related) => {
    linkModalRef.current.show({ id, name, related })
  }

  function isAdmin() {
    return role > ROLES.USER
  }

  function isTrain(type) {
    return type === TYPES.TRAINING
  }

  function isDone(state) {
    return state === STATES.DONE
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
        <span className={s.infoItem}><span className={s.infoLabel}>{t('image.list.item.type')}</span>{getImageTypeLabel(item.type)}</span>
        <span className={s.infoItem}><span className={s.infoLabel}>{t('image.list.item.url')}</span>{item.url}</span>
        <span className={s.infoItem}><span className={s.infoLabel}>{t('image.list.item.desc')}</span>{item.description}</span>
      </Space>
      { isTrain(item.type) && item.related?.length ? <div className={s.related}><span>{t('image.list.item.related')}</span><ImagesLink images={item.related} /></div> : null }
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
      {isAdmin() ? addBtn : null}
      <List
        className={s.list}
        dataSource={images}
        renderItem={renderItem}
      />
      <Pagination className={s.pager} onChange={pageChange}
        defaultCurrent={1} defaultPageSize={query.limit} total={total}
        showTotal={() => t('image.list.total', { total })}
        showQuickJumper showSizeChanger />
      <ShareModal ref={shareModalRef} />
      <RelateModal ref={linkModalRef} ok={relateOk} />
      <Del ref={delRef} ok={delOk} />
    </div>
  )
}


const props = (state) => {
  return {
    role: state.user.role,
    username: state.user.username,
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
