import React, { useEffect, useRef, useState } from 'react'
import { connect } from 'dva'
import { useHistory } from 'umi'
import { List, Skeleton, Space, Button, Pagination, Col, Row, Alert } from 'antd'

import t from '@/utils/t'
import { HIDDENMODULES } from '@/constants/common'
import { ROLES } from '@/constants/user'
import { TYPES, STATES, getImageTypeLabel, imageIsPending } from '@/constants/image'
import { getProjectTypeLabel } from '@/constants/project'

import RelateModal from './relate'
import Del from './del'
import ImagesLink from './imagesLink'
import StateTag from '@/components/image/StateTag'

import s from './list.less'
import { EditIcon, DeleteIcon, AddIcon, MoreIcon, PublishIcon, LinkIcon } from '@/components/common/Icons'
import { FailIcon, SuccessIcon } from '@/components/common/Icons'
import { LoadingOutlined } from '@ant-design/icons'

const initQuery = {
  name: undefined,
  type: undefined,
  current: 1,
  offset: 0,
  limit: 20,
}

// todo identify annotation types supported
const ImageList = ({ role, filter, getImages }) => {
  const history = useHistory()
  const [images, setImages] = useState([])
  const [total, setTotal] = useState(1)
  const [query, setQuery] = useState(initQuery)
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
    setQuery((old) => ({ ...old, current, limit, offset }))
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
    const { id, name, state, functions, url, related, description } = record

    const menus = [
      {
        key: 'link',
        label: t('image.action.link'),
        onclick: () => link(id, name, related),
        hidden: () => !isTrain(functions) || !isDone(state),
        icon: <LinkIcon />,
      },
      {
        key: 'publish',
        label: t('image.action.publish'),
        onclick: () => history.push(`/home/public_image/publish?name=${name}&image_addr=${url}&description=${description}`),
        hidden: () => !isAdmin() || !isDone(state),
        icon: <PublishIcon />,
      },
      {
        key: 'edit',
        label: t('image.action.edit'),
        onclick: () => history.push(`/home/image/add/${id}`),
        icon: <EditIcon />,
      },
      {
        key: 'del',
        label: t('image.action.del'),
        hidden: () => !isAdmin() || imageIsPending(state),
        onclick: () => del(id, name),
        icon: <DeleteIcon />,
      },
    ]

    const detail = {
      key: 'detail',
      label: t('image.action.detail'),
      onclick: () => history.push(`/home/image/detail/${id}`),
      icon: <MoreIcon />,
    }
    return isAdmin() ? [...menus, detail] : [detail]
  }

  const del = (id, name) => {
    delRef.current.del(id, name)
  }

  const delOk = (id) => {
    setImages(images.filter((image) => image.id !== id))
    setTotal((old) => old - 1)
    getData()
  }

  const relateOk = () => getData()

  const link = (id, name, related) => {
    linkModalRef.current.show({ id, name, related })
  }

  const isAdmin = () => role > ROLES.USER

  const isTrain = (functions = []) => functions.indexOf(TYPES.TRAINING) >= 0

  const isDone = (state) => state === STATES.DONE

  const more = (item) => {
    return (
      <Space>
        {moreList(item)
          .filter((menu) => !(menu.hidden && menu.hidden()))
          .map((action) => (
            <a type="link" className={action.className} key={action.key} onClick={action.onclick} title={action.label}>
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
    return <span className={s.stateIcon}>{states[state]}</span>
  }

  const objectTypeLabel = (type) => {
    const cls = getProjectTypeLabel(type)
    const label = getProjectTypeLabel(type, true)
    return type && cls ? <span className={`extraTag ${cls}`}>{t(label)}</span> : null
  }

  const liveCodeState = (live) => {
    return <span className={live ? s.remote : s.local}>{t(live ? 'image.livecode.label.remote' : 'image.livecode.label.local')}</span>
  }

  const addBtn = (
    <div className={s.addBtn} onClick={() => history.push('/home/image/add')}>
      <AddIcon />
      {t('image.new.label')}
    </div>
  )

  const renderItem = (item) => {
    const title = (
      <Row wrap={false}>
        <Col flex={1}>
          <Space>
            <span>{item.name}</span>
            {objectTypeLabel(item.objectType)}
            <StateTag state={item.state} />
            {isDone(item.state) && !HIDDENMODULES.LIVECODE ? liveCodeState(item.liveCode) : null}
          </Space>
        </Col>
        <Col onClick={e => e.stopPropagation()}>{more(item)}</Col>
      </Row>
    )
    const type = isTrain(item.functions) ? 'train' : 'mining'
    const desc = (
      <Row>
        <Col className={s.desc} flex={1}>
          <Space className={s.info} wrap={true}>
            <span className={s.infoItem} style={{ minWidth: 200 }}>
              <span className={s.infoLabel}>{t('image.list.item.type')}</span>
              {getImageTypeLabel(item.functions)
                .map((label) => t(label))
                .join(', ')}
            </span>
            <span className={s.infoItem} style={{ minWidth: 300 }}>
              <span className={s.infoLabel}>{t('image.list.item.url')}</span>
              {item.url}
            </span>
            <span className={s.infoItem}>
              <span className={s.infoLabel}>{t('image.list.item.desc')}</span>
              {item.description}
            </span>
          </Space>
          {isTrain(item.functions) && item.related?.length ? (
            <div className={s.related}>
              <span>{t('image.list.item.related')}</span>
              <ImagesLink images={item.related} />
            </div>
          ) : null}
        </Col>
      </Row>
    )

    return (
      <List.Item className={item.state ? 'success' : 'failure'} onClick={() => history.push(`/home/image/detail/${item.id}`)}>
        <Skeleton active loading={item.loading}>
          <List.Item.Meta title={title} description={desc}></List.Item.Meta>
        </Skeleton>
      </List.Item>
    )
  }

  return (
    <div className={s.imageContent}>
      {isAdmin() ? addBtn : <Alert message={t('image.add.image.tip.admin')} type="warning" showIcon />}
      <List className="list" dataSource={images} renderItem={renderItem} />
      <Pagination
        className="pager"
        onChange={pageChange}
        current={query.current}
        defaultCurrent={query.current}
        defaultPageSize={query.limit}
        total={total}
        showTotal={() => t('image.list.total', { total })}
        showQuickJumper
        showSizeChanger
      />
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
