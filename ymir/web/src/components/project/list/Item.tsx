import { FC, ReactNode } from 'react'
import { List, Skeleton, Space, Col, Row, Popover } from 'antd'
import { useHistory } from 'umi'

import t from '@/utils/t'
import { getProjectTypeLabel } from '@/constants/project'
import { getStepLabel, STEP } from '@/constants/iteration'

import KeywordsItem from '../KeywordsItem'

import s from './item.less'

type Props = {
  project: YModels.Project,
  more?: ReactNode,
}
const Item: FC<Props> = ({ project, more }) => {
  const history = useHistory()
  const typeLabel = getProjectTypeLabel(project.type)
  const title = (
    <Row wrap={false} className="title">
      <Col flex={1}>
        <Space>
          <span className={s.name}>
            <span>{project.name}</span>
            <span className={`extraTag ${[typeLabel]}`}>{t(project.typeLabel)}</span>
            {project.isExample ? <span className="extraTag example">{t('project.example')}</span> : null}
          </span>
          <span className="titleItem">
            <span className="titleLabel">{t('project.train_classes')}:</span>
            <span className="titleContent">
              <KeywordsItem keywords={project.keywords} />
            </span>
          </span>
          {project.enableIteration ? (
            <span className="titleItem">
              <span className="titleLabel">{t('project.iteration.current')}:</span>
              <span className="titleContent emphasis">{t(getStepLabel(project.currentStep as STEP, project.round))}</span>
            </span>
          ) : null}
        </Space>
      </Col>
      <Col>{more}</Col>
    </Row>
  )

  const tipContent = (
    <div>
      <div>
        {t('project.train_set')}: {project.trainSet?.name}
      </div>
      <div>
        {t('project.test_set')}: {project.testSet?.name}
      </div>
      <div>
        {t('project.mining_set')}: {project.miningSet?.name}
      </div>
    </div>
  )

  const desc = (
    <>
      <Row className="content" justify="center">
        <Col span={4} className={s.stats}>
          <div className="contentLabel">{t('project.tab.set.title')}</div>
          <div className="contentContent">{project.setCount}</div>
        </Col>
        <Col span={4} className={s.stats}>
          <div className="contentLabel">{t('project.tab.model.title')}</div>
          <div className="contentContent">{project.modelCount}</div>
        </Col>
        <Col flex={1} className={s.stats}>
          <div className="contentLabel">
            {t('project.train_set')}|{t('project.test_set')}|{t('project.mining_set')}
          </div>
          <div className="sets">
            <Popover placement="right" content={tipContent}>
              <span className="setLabel">{project.trainSet?.name}</span>
              <span>|</span>
              <span className="setLabel">{project.testSet?.name}</span>
              <span>|</span>
              <span className="setLabel">{project.miningSet?.name}</span>
            </Popover>
          </div>
        </Col>

        {project.enableIteration ? (
          <Col span={4} className={s.stats}>
            <div className="contentLabel">{t('project.iteration.number')}</div>
            <div className="contentContent">
              <span className="currentIteration">{project.round}</span>
            </div>
          </Col>
        ) : null}
      </Row>
      <Row>
        <Col flex={1}>
          <span className="bottomLabel">{t('project.content.desc')}:</span> <span className={s.bottomContent}>{project.description}</span>
        </Col>
        <Col>
          <span className="bottomContent">{project.createTime}</span>
        </Col>
      </Row>
    </>
  )

  return (
    <List.Item
      onClick={() => {
        history.push(`/home/project/${project.id}/detail`)
      }}
    >
      <Skeleton active loading={!project.id}>
        <List.Item.Meta title={title} description={desc}></List.Item.Meta>
      </Skeleton>
    </List.Item>
  )
}

export default Item
