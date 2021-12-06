import { Link } from 'umi'
import { useState } from 'react'
import { Row, Col } from "antd"
import { connect } from "dva"

import t from '@/utils/t'
import commonStyles from './common.less'
import LogoRight from '@/assets/logo_right.png'

function QuickActions({ setGuideVisible }) {
  const [qaVisible, setQaVisible] = useState(false)
  const [top, setTop] = useState('50%')

  function drag(ev) {
    if (ev.clientY) {
      setTop(ev.clientY)
    }
  }
  function dragEnd(ev) {
    setTop(ev.clientY)
  }

  return <div className={commonStyles.quickActions} style={{ top }} onMouseEnter={() => setQaVisible(true)} onMouseLeave={() => setQaVisible(false)}>
  <Row className={commonStyles.qaContent} align='middle'>
    {qaVisible ? <>
    <Col className={commonStyles.quickAction}>
      <Link className={commonStyles.action} to={{ pathname: '/home/dataset/add'}}>{t('common.qa.action.import', { br: <br /> })}</Link>
    </Col>
    <Col className={commonStyles.quickAction}>
      <Link className={commonStyles.action} to='/home/task/train'>{t('common.qa.action.train', { br: <br /> })}</Link>
    </Col>
    <Col className={commonStyles.quickAction}>
      <a className={commonStyles.action} to={null} onClick={() => setGuideVisible(true)}>{t('common.qa.action.guide', { br: <br /> })}</a>
    </Col>
    </> : null }
    <Col className={commonStyles.logo} onDrag={(ev) => drag(ev)} onDragEnd={(ev) => dragEnd(ev)}>
    <img src={LogoRight} />
    </Col>
  </Row>
</div>
}

const actions = (dispatch) => {
  return {
    setGuideVisible(visible) {
      return dispatch({
        type: 'user/setGuideVisible',
        payload: visible,
      })
    }
  }
}
export default connect(null, actions)(QuickActions)
