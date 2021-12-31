import React, { useEffect, useRef, useState } from "react"
import { Descriptions, List, Space, Tag, Card, Button, Row, Col } from "antd"
import { connect } from 'dva'
import { useParams, Link, useHistory } from "umi"

import t from "@/utils/t"
import Breadcrumbs from "../../components/common/breadcrumb"
import { TYPES, STATES, getImageTypeLabel, getImageStateLabel } from '@/constants/image'
import { ROLES } from '@/constants/user'
import LinkModal from "./components/relate"
import ShareModal from "./components/share"
import Del from './components/del'
import styles from "./detail.less"
import { EditIcon, VectorIcon, TrainIcon, } from '@/components/common/icons'
import ImagesLink from "./components/imagesLink"

const { Item } = Descriptions

function ImageDetail({ role, getImage }) {
  const { id } = useParams()
  const history = useHistory()
  const [image, setImage] = useState({ id })
  const shareModalRef = useRef(null)
  const linkModalRef = useRef(null)
  const delRef = useRef(null)

  useEffect(async () => {
    const result = await getImage(id)
    if (result) {
      // console.log('image: ', result)
      setImage(result)
    }
  }, [id])

  function relateImage() {
    const { name, related } = image
    linkModalRef.current.show({ id, name, related })
  }
  const share = () => {
    shareModalRef.current.show(id, image.name)
  }

  const del = () => {
    delRef.current.del(id, image.name)
  }

  const delOk = () => {
    history.push('/home/image')
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

  function renderConfig(config = {}) {
    return Object.keys(config).map(key => <Row key={key}>
      <Col style={{ width: 200, fontWeight: 'bold' }}>{key}:</Col>
      <Col>{config[key]}</Col>
    </Row>)
  }

  function renderTaskBtn() {
    const type = isTrain(image.type) ? 'train' : 'mining'
    return <Button onClick={() => history.push(`/home/task/${type}?image=${id}`)}>
      {isTrain(image.type) ? <TrainIcon /> : <VectorIcon />} {t(`image.list.${type}.btn`)}
    </Button>
  }

  function renderTitle() {
    return (
      <Row>
        <Col flex={1}>{image.name} <Link to={`/home/image/add/${id}`}><EditIcon /></Link></Col>
        <Col><Button type='link' onClick={() => history.goBack()}>{t('common.back')}&gt;</Button></Col>
      </Row>
    )
  }

  return (
    <div className={styles.imageDetail}>
      <Breadcrumbs />
      <Card title={renderTitle()}>
        <Descriptions bordered column={2} labelStyle={{ width: '200px' }} title={t('image.detail.title')}>
          <Item label={t('image.detail.label.name')}>{image.name}</Item>
          <Item label={t('image.detail.label.type')}>{getImageTypeLabel(image.type)}</Item>
          <Item label={t('image.detail.label.url')}>{image.url}</Item>
          <Item label={t('image.detail.label.share')}>{image.is_shared ? t('common.yes') : t('common.no')}</Item>
          <Item label={t('image.detail.label.related')} span={2}>
            <Row><Col flex={1}><ImagesLink images={image.related} /></Col>
              {isAdmin() ? <Col><Button type="primary" onClick={() => relateImage()}>{t('image.detail.relate')}</Button></Col> : null}
            </Row>
          </Item>
          <Item label={t('image.detail.label.config')} span={2}>
            {renderConfig(image.config)}
          </Item>
          <Item label={t('image.detail.label.state')} span={2}>{getImageStateLabel(image.state)}</Item>
          <Item label={''} span={2}><Space>
            {renderTaskBtn()}
            {isAdmin() ? <>
              <Button onClick={share}>{t('image.action.share')}</Button>
              <Button onClick={del}>{t('common.del')}</Button> </> : null}
          </Space></Item>
        </Descriptions>
      </Card>
      <LinkModal ref={linkModalRef} />
      <ShareModal ref={shareModalRef} />
      <Del ref={delRef} ok={delOk} />
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
    getImage(id) {
      return dispatch({
        type: 'image/getImage',
        payload: id,
      })
    },
  }
}

export default connect(props, actions)(ImageDetail)
