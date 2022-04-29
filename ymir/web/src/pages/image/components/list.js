
import React, { useEffect, useRef, useState } from "react"
import { connect } from 'dva'
import { useHistory } from "umi"
import { List, Skeleton, Space, Button, Pagination, Col, Row, } from "antd"

import t from "@/utils/t"
import { ROLES } from '@/constants/user'
import { TYPES, STATES, getImageTypeLabel, imageIsPending } from '@/constants/image'
import ShareModal from "./share"
import RelateModal from './relate'
import Del from './del'
import s from "./list.less"
import { VectorIcon, TrainIcon, TipsIcon, EditIcon, DeleteIcon, AddIcon, MoreIcon, ShareIcon, LinkIcon } from "@/components/common/icons"
import ImagesLink from "./imagesLink"
import { FailIcon, SuccessIcon } from "@/components/common/icons"
import { LoadingOutlined } from '@ant-design/icons'

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

  const pageChange = (current, pageSize) => {
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
    const { id, name, state, functions, url, related, is_shared } = record

    const menus = [
      {
        key: "link",
        label: t("image.action.link"),
        onclick: () => link(id, name, related),
        hidden: () => (!isTrain(functions) || !isDone(state)),
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
        hidden: () => imageIsPending(state),
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

  const del = (id, name) => {
    delRef.current.del(id, name)
  }

  const delOk = (id) => {
    setImages(images.filter(image => image.id !== id))
    setTotal(old => old - 1)
    getData()
  }

  const relateOk = () => getData()

  const shareOk = () => getData()

  const share = (id, name) => shareModalRef.current.show(id, name)

  const link = (id, name, related) => {
    linkModalRef.current.show({ id, name, related })
  }

  const isAdmin = () => role > ROLES.USER

  const isTrain = (functions = []) => functions.indexOf(TYPES.TRAINING) >= 0

  const isDone = (state) => state === STATES.DONE

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

  const imageState = (state) => {
    const states = {
      [STATES.PENDING]: <LoadingOutlined style={{ color: 'rgba(54, 203, 203, 1)', fontSize: 16 }} />,
      [STATES.DONE]: <SuccessIcon style={{ color: 'rgba(54, 203, 203, 1)', fontSize: 16 }} />,
      [STATES.ERROR]: <FailIcon style={{ color: 'rgba(242, 99, 123, 1)', fontSize: 16 }} />,
    }
    return states[state]
  }

  const addBtn = (
    <div className={s.addBtn} onClick={() => history.push('/home/image/add')}><AddIcon />{t('image.new.label')}</div>
  )

  const renderItem = (item) => {
    const title = <Row wrap={false}>
      <Col flex={1}>{item.name}<span className={s.stateIcon}>{imageState(item.state)}</span></Col>
      <Col>{more(item)}</Col>
    </Row>
    const type = isTrain(item.functions) ? 'train' : 'mining'
    const desc = <Row><Col className={s.desc} flex={1}>
      <Space className={s.info}>
        <span className={s.infoItem}><span className={s.infoLabel}>{t('image.list.item.type')}</span>{getImageTypeLabel(item.functions).map(label => t(label)).join(', ')}</span>
        <span className={s.infoItem}><span className={s.infoLabel}>{t('image.list.item.url')}</span>{item.url}</span>
        <span className={s.infoItem}><span className={s.infoLabel}>{t('image.list.item.desc')}</span>{item.description}</span>
      </Space>
      {isTrain(item.functions) && item.related?.length ? <div className={s.related}><span>{t('image.list.item.related')}</span><ImagesLink images={item.related} /></div> : null}
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
        className='list'
        dataSource={images}
        renderItem={renderItem}
      />
      <Pagination className='pager' onChange={pageChange}
        defaultCurrent={1} defaultPageSize={query.limit} total={total}
        showTotal={() => t('image.list.total', { total })}
        showQuickJumper showSizeChanger />
      <ShareModal ref={shareModalRef} ok={shareOk} />
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
