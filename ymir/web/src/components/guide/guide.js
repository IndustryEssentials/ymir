import { useEffect, useRef, useState } from 'react'
import { connect } from "dva"
import { Row, Col, Modal, Card, Button, Checkbox } from 'antd'
import { useHistory } from 'umi'

import t from '@/utils/t'
import s from './guide.less'
import { NoSjjIcon, TrainIcon, ExcavateIcon, TaggingIcon, BookIcon } from '@/components/common/icons'

const Guide = ({ visible, neverShow, setGuideVisible, setNeverShow }) => {
  // const [neverAutoShow, setNeverAutoShow] = useState(false)
  const history = useHistory()

  // useEffect(() => {
  //   setNeverShow(neverAutoShow)
  // }, [neverAutoShow])

  function go(url) {
    setGuideVisible(false)
    history.push(url)
  }

  function close() {
    setGuideVisible(false)
  }

  return visible ? (
    <Modal
      className={s.guide}
      visible={visible}
      centered
      footer={null}
      width={'80%'}
      onCancel={close}
    >
      <div className={s.mainTitle}>
        <h3><BookIcon style={{ fontSize: 28 }} />{t('common.guide.title')}</h3>
      </div>
      <Row className={s.mainSteps} gutter={10}>
        <Col className={s.step}>
          <Card className={s.stepBox} hoverable onClick = {() => go({ pathname: '/home/dataset/add'})}>
            <h2><span className={s.stepTitle}>{t('common.guide.step1.title')}</span></h2>
            <p><NoSjjIcon className={s.stepIcon} /></p>
            <p className={s.stepTip}>{t('common.guide.step1.content')}</p>
            <p><Button className={s.stepButton}>{t('common.guide.step1.btn')}</Button></p>
          </Card>
        </Col>
        <Col className={s.step}>
          <Card className={s.stepBox} hoverable onClick = {() => go('/home/task/label')}>
            <h2><span className={s.stepTitle}>{t('common.guide.step6.title')}</span></h2>
            <p><TaggingIcon className={s.stepIcon} /></p>
            <p className={s.stepTip}>{t('common.guide.step6.content')}</p>
            <p><Button className={s.stepButton}>{t('common.guide.step4.btn')}</Button></p>
          </Card>
        </Col>
        <Col className={s.step}>
          <Card className={s.stepBox} hoverable onClick = {() => go('/home/task/train')}>
            <h2><span className={s.stepTitle}>{t('common.guide.step2.title')}</span></h2>
            <p><TrainIcon className={s.stepIcon} /></p>
            <p className={s.stepTip}>{t('common.guide.step2.content')}</p>
            <p><Button className={s.stepButton}>{t('common.guide.step2.btn')}</Button></p>
          </Card>
        </Col>
        <Col className={s.step}>
          <Card className={s.stepBox} hoverable onClick = {() => go('/home/task/mining')}>
            <h2><span className={s.stepTitle}>{t('common.guide.step3.title')}</span></h2>
            <p><ExcavateIcon className={s.stepIcon} /></p>
            <p className={s.stepTip}>{t('common.guide.step3.content')}</p>
            <p><Button className={s.stepButton}>{t('common.guide.step3.btn')}</Button></p>
          </Card>
        </Col>
        <Col className={s.step}>
          <Card className={s.stepBox} hoverable onClick = {() => go('/home/task/label')}>
            <h2><span className={s.stepTitle}>{t('common.guide.step4.title')}</span></h2>
            <p><TaggingIcon className={s.stepIcon} /></p>
            <p className={s.stepTip}>{t('common.guide.step4.content')}</p>
            <p><Button className={s.stepButton}>{t('common.guide.step4.btn')}</Button></p>
          </Card>
        </Col>
        <Col className={s.step}>
          <Card className={s.stepBox} hoverable onClick = {() => go('/home/task/train')}>
            <h2><span className={s.stepTitle}>{t('common.guide.step5.title')}</span></h2>
            <p><TrainIcon className={s.stepIcon} /></p>
            <p className={s.stepTip}>{t('common.guide.step5.content')}</p>
            <p><Button className={s.stepButton}>{t('common.guide.step2.btn')}</Button></p>
          </Card>
        </Col>
      </Row>
      <p><Checkbox defaultChecked={neverShow} onChange={ ({ target }) => setNeverShow(target.checked)}>{t('common.guide.nevershow')}</Checkbox></p>
    </Modal>
  ) : null
}

const props = (state) => {
  return {
    visible: state.user.guideVisible,
    neverShow: state.user.neverShow,
  }
}

const actions = (dispatch) => {
  return {
    setGuideVisible(visible) {
      return dispatch({
        type: 'user/setGuideVisible',
        payload: visible,
      })
    },
    setNeverShow(never) {
      return dispatch({
        type: 'user/setNeverShow',
        payload: never,
      })
    },
  }
}
export default connect(props, actions)(Guide)
