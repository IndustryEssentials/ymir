
import React, { useEffect, useState } from "react"
import { connect } from 'dva'
import { useHistory } from "umi"
import { List, Skeleton, Space, Col, Row, } from "antd"

import t from "@/utils/t"
import { ROLES } from '@/constants/user'
import s from "./list.less"
import { CopyIcon, NavHomeIcon, SuccessIcon, UserSharedIcon } from "@/components/common/icons"


const ImageList = ({ role, getShareImages }) => {

  const history = useHistory()
  const [images, setImages] = useState([])

  /** use effect must put on the top */
  useEffect(() => {
    fetchShareImage()
  }, [])

  async function fetchShareImage() {

    const result = await getShareImages()
    if (result) {
      setImages(result)
    }
  }

  const moreList = (record = {}) => {

    const menus = [
      {
        key: "copy",
        label: t("image.action.copy"),
        onclick: () => copy(record),
        icon: <CopyIcon />,
      },
    ]
    return isAdmin() ? menus : []
  }

  function copy (record) {
    history.push({pathname: '/home/image/add', state: { record }})
  }

  function isAdmin() {
    return role > ROLES.USER
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

  const renderItem = (item) => {
    const title = <Row wrap={false}>
      <Col flex={1}>{item.docker_name}</Col>
      <Col>{more(item)}</Col>
    </Row>
    const desc = <Row><Col className={s.desc} flex={1}>
      <Space className={s.info} >
        <span className={s.infoItem}><span className={s.infoLabel}>{t('image.list.item.type')}</span>{item.functions}</span>
        <span className={s.infoItem}><span className={s.infoLabel}>{t('image.list.item.desc')}</span>{item.description}</span>
      </Space>
      <div className={s.related}>
        <span><NavHomeIcon title={t('image.list.item.org')} /> </span>{item.organization}
        <UserSharedIcon title='Contributor' title={t('image.list.item.contributor')} /> {item.contributor}
      </div>
    </Col>
    </Row>

    return <List.Item>
      <Skeleton active loading={item.loading}>
        <List.Item.Meta title={title} description={desc}>
        </List.Item.Meta>
      </Skeleton>
    </List.Item>
  }

  return (
    <div className={s.imageContent}>
      <List
        className='list'
        dataSource={images}
        renderItem={renderItem}
      />
      <div className={s.pager}>Total: {images.length}</div>
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
    getShareImages: (payload) => {
      return dispatch({
        type: 'image/getShareImages',
        payload,
      })
    },
  }
}

export default connect(props, actions)(ImageList)
