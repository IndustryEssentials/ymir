import React, { useEffect, useRef, useState } from "react"
import { Descriptions, List, Space, Tag, Card, Button, Row, Col } from "antd"
import { connect } from 'dva'
import { useParams, Link, useHistory } from "umi"

import t from "@/utils/t"
import Breadcrumbs from "@/components/common/breadcrumb"
import { TYPES, STATES, getImageTypeLabel } from '@/constants/image'
import { ROLES } from '@/constants/user'
import LinkModal from "./components/relate"
import ShareModal from "./components/share"
import Del from './components/del'
import styles from "./detail.less"
import { EditIcon, VectorIcon, TrainIcon, } from '@/components/common/icons'
import ImagesLink from "./components/imagesLink"
import StateTag from '../../components/task/stateTag'

const { Item } = Descriptions

function ImageDetail({ role, getImage }) {
  const { id } = useParams()
  const history = useHistory()
  const [image, setImage] = useState({ id })
  const shareModalRef = useRef(null)
  const linkModalRef = useRef(null)
  const delRef = useRef(null)

  useEffect(async () => {
    fetchImage()
  }, [id])

  async function fetchImage() {
    const result = await getImage(id)
    if (result) {
      setImage(result)
    }
  }

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

  function isDone() {
    return image.state === STATES.DONE
  }

  function isError() {
    return image.state === STATES.ERROR
  }

  function renderConfigs(configs = []) {
    return configs.map(({config, type }) => {
      return <>
      <h3>{t(getImageTypeLabel([type])[0])}</h3>
      <div>{renderConfig(config)}</div>
      </>
    })
  }

  function renderConfig(config = {}) {
    return Object.keys(config).map(key => <Row key={key}>
      <Col style={{ width: 200, fontWeight: 'bold' }}>{key}:</Col>
      <Col>{config[key]}</Col>
    </Row>)
  }

  function renderTaskBtn() {
    return image.functions.map(func => {
      const type = isTrain(func) ? 'train' : 'mining'
      return <Button onClick={() => history.push(`/home/task/${type}?image=${id}`)}>
        {isTrain(func) ? <TrainIcon /> : <VectorIcon />} {t(`image.list.${type}.btn`)}
      </Button>
    })
  }

  function renderTitle() {
    return (
      <Row>
        <Col flex={1}>{image.name} { isAdmin() ? <Link to={`/home/image/add/${id}`}><EditIcon /></Link> : null }</Col>
        <Col><Button type='link' onClick={() => history.goBack()}>{t('common.back')}&gt;</Button></Col>
      </Row>
    )
  }

  return (
    <div className={styles.imageDetail}>
      <Breadcrumbs />
      <Card title={renderTitle()}>
        <div className='infoTable' >
        <Descriptions bordered column={2} labelStyle={{ width: '200px'}} title={t('image.detail.title')}>
          <Item label={t('image.detail.label.name')}>{image.name}</Item>
          <Item label={t('image.detail.label.type')}>{getImageTypeLabel(image.functions).map(label => t(label)).join(',')}</Item>
          <Item label={t('image.detail.label.url')}>{image.url}</Item>
          <Item label={t('image.detail.label.share')}>{image.is_shared ? t('common.yes') : t('common.no')}</Item>
          <Item label={t('image.detail.label.related')} span={2}>
            <Row><Col flex={1}><ImagesLink images={image.related} /></Col>
              {isAdmin() && isDone() ? <Col><Button type="primary" onClick={() => relateImage()}>{t('image.detail.relate')}</Button></Col> : null}
            </Row>
          </Item>
          <Item label={t('image.detail.label.config')} span={2}>
            {renderConfigs(image.configs)}
          </Item>
          <Item label={t('image.detail.label.state')} span={2}> <StateTag state={image.state} /> </Item>
         
          <Item label={''} span={2}><Space>
            <Button hidden={!isAdmin() || !isDone()} onClick={share}>{t('image.action.share')}</Button>
            <Button hidden={!isAdmin() || (!isDone() && !isError())} onClick={del}>{t('common.del')}</Button>
          </Space></Item>
        </Descriptions>
        </div>
      </Card>
      <LinkModal ref={linkModalRef} ok={() => fetchImage()} />
      <ShareModal ref={shareModalRef} ok={() => fetchImage()} />
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
