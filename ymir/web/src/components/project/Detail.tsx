import { FC } from 'react'
import { Button, Col, Row, Space } from 'antd'
import t from '@/utils/t'
import s from './detail.less'
import TestingSet from './TestingSet'
import { useHistory } from 'umi'
import ObjectTypeTag from './ObjectTypeTag'
import Stats from './Stats'

type Props = {
  project?: YModels.Project
  type?: 'dataset' | 'model'
  back?: boolean
}

const Detail: FC<Props> = ({ project, type, back }) => {
  const history = useHistory()
  const backBtn = <Button className={s.back} onClick={() => history.goBack()}>{t('common.back')}</Button>
  return project ? (
    <div className={s.header}>
      <Row>
        <Col flex={1}>

      <Space className={s.detailPanel} wrap size={16}>
        <span className={s.name}>{project.name}</span>
        <ObjectTypeTag type={project.type} />
        {project.description ? (
          <span>
            {t('project.detail.desc')}: {project.description}
          </span>
        ) : null}
      </Space>
        </Col>
        <Col span={12} style={{ borderLeft: '1px solid #d2def2'}}>
        {type ? <Stats project={project} type={type} /> : back ? backBtn : null}
        </Col>
      </Row>
      <TestingSet project={project} />
    </div>
  ) : null
}

export default Detail
