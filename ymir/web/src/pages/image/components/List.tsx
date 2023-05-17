import React, { FC, useEffect, useRef, useState } from 'react'
import { useHistory, useSelector } from 'umi'
import { List, Skeleton, Space, Button, Pagination, Col, Row, Alert } from 'antd'

import t from '@/utils/t'
import { HIDDENMODULES, validState } from '@/constants/common'
import { isAdmin } from '@/constants/user'
import { TYPES, STATES, getImageTypeLabel, isSampleImage } from '@/constants/image'
import { getProjectTypeLabel, ObjectType } from '@/constants/project'
import useRequest from '@/hooks/useRequest'

import RelateModal, { RefProps } from './Relate'
import Del, { RefProps as DelRefProps } from '@/components/image/Del'
import ImagesLink from './ImagesLink'
import StateTag from '@/components/image/StateTag'
import OfficialTag from '@/components/image/OfficialTag'

import s from './list.less'
import { EditIcon, DeleteIcon, AddIcon, MoreIcon, PublishIcon, LinkIcon } from '@/components/common/Icons'
import { Image } from '@/constants'
import { QueryParams } from '@/services/typings/image.d'
import { List as ListType } from '@/models/typings/common.d'

const initQuery = {
  name: undefined,
  type: undefined,
  offset: 0,
  limit: 20,
}

const ImageList: FC<{ filter: () => void }> = ({ filter }) => {
  const history = useHistory()
  const [images, setImages] = useState<Image[]>([])
  const [total, setTotal] = useState(1)
  const [query, setQuery] = useState(initQuery)
  const [current, setCurrent] = useState(1)
  const linkModalRef = useRef<RefProps>(null)
  const delRef = useRef<DelRefProps>(null)
  const role = useSelector(({ user }) => user.user.role)
  const { data: remoteImages, run: getImages } = useRequest<ListType<Image>, [QueryParams]>('image/getImages')

  /** use effect must put on the top */
  useEffect(() => {
    getData()
  }, [query])

  useEffect(() => {
    if (remoteImages) {
      const { items, total } = remoteImages
      setImages(items)
      setTotal(total)
    }
  }, [remoteImages])

  useEffect(() => {
    JSON.stringify(filter) !== JSON.stringify(query) && setQuery({ ...query, ...filter })
  }, [filter])

  const pageChange = (current: number, pageSize: number) => {
    const limit = pageSize
    const offset = (current - 1) * pageSize
    setCurrent(current)
    setQuery((old) => ({ ...old, limit, offset }))
  }

  const getData = () => getImages(query)

  const moreList = (record: Image): YComponents.Action[] => {
    const { id, name, state, functions, url, related, description } = record

    const menus = [
      {
        key: 'link',
        label: t('image.action.link'),
        onclick: () => link(record),
        hidden: () => !isTrain(functions) || !validState(state),
        icon: <LinkIcon />,
      },
      {
        key: 'publish',
        label: t('image.action.publish'),
        onclick: () => history.push(`/home/public_image/publish?name=${name}&image_addr=${url}&description=${description}`),
        hidden: () => !isAdmin(role) || !validState(state),
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
        hidden: () => !isAdmin(role) || isSampleImage(record),
        onclick: () => del(record),
        icon: <DeleteIcon />,
      },
    ]

    const detail = {
      key: 'detail',
      label: t('image.action.detail'),
      onclick: () => history.push(`/home/image/detail/${id}`),
      icon: <MoreIcon />,
    }
    return isAdmin(role) ? [...menus, detail] : [detail]
  }

  const del = ({ id, name }: Image) => {
    delRef.current?.del(id, name)
  }

  const delOk = (id: number) => {
    setImages(images.filter((image) => image.id !== id))
    setTotal((old) => old - 1)
    getData()
  }

  const relateOk = () => getData()

  const link = ({ id, name, related }: Image) => {
    linkModalRef.current?.show({ id, name, related })
  }

  const isTrain = (functions: number[] = []) => functions.indexOf(TYPES.TRAINING) >= 0

  const more = (item: Image) => {
    return (
      <Space>
        {moreList(item)
          .filter((menu) => !(menu.hidden && menu.hidden()))
          .map((action) => (
            <a type="link" key={action.key} onClick={() => action.onclick && action.onclick()} title={action.label}>
              {action.icon}
            </a>
          ))}
      </Space>
    )
  }

  const objectTypeLabel = (types: ObjectType[]) =>
    types.map((type) => {
      const cls = getProjectTypeLabel(type)
      const label = getProjectTypeLabel(type, true)
      return type && cls ? (
        <span key={type} className={`extraTag ${cls}`}>
          {t(label)}
        </span>
      ) : null
    })

  const liveCodeState = (live?: boolean) => {
    return <span className={live ? s.remote : s.local}>{t(live ? 'image.livecode.label.remote' : 'image.livecode.label.local')}</span>
  }

  const addBtn = (
    <div className={s.addBtn} onClick={() => history.push('/home/image/add')}>
      <AddIcon />
      {t('image.new.label')}
    </div>
  )

  const renderItem = (item: Image) => {
    const title = (
      <Row wrap={false}>
        <Col flex={1}>
          <Space>
            <span>{item.name}</span>
            <OfficialTag official={item.official} />
            {objectTypeLabel(item.objectTypes)}
            <StateTag state={item.state} code={item.errorCode} />
            {validState(item.state) && !HIDDENMODULES.LIVECODE ? liveCodeState(item.liveCode) : null}
          </Space>
        </Col>
        <Col onClick={(e) => e.stopPropagation()}>{more(item)}</Col>
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
        <List.Item.Meta title={title} description={desc}></List.Item.Meta>
      </List.Item>
    )
  }

  return (
    <div className={s.imageContent}>
      {isAdmin(role) ? addBtn : <Alert message={t('image.add.image.tip.admin')} type="warning" showIcon />}
      <List className="list" dataSource={images} renderItem={renderItem} />
      <Pagination
        className="pager"
        onChange={pageChange}
        current={current}
        defaultCurrent={current}
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

export default ImageList
