import { FC, ReactNode } from 'react'
import { Col, Row, Space } from 'antd'

import t from '@/utils/t'
import { getStepLabel, STEP } from '@/constants/iteration'

import ObjectTypeTag from '@/components/project/ObjectTypeTag'

import s from '../detail.less'
import { Project } from '@/constants'

const ProjectDetail: FC<{ project: Project; extra?: ReactNode }> = ({ project, extra }) => {
  const id = project.id

  return (
    <div className={s.detailContainer}>
      <Row>
        <Col flex={1}>
          <Space className={s.detailPanel} wrap size={16}>
            <span className={s.name}>{project.name}</span>
            <ObjectTypeTag type={project.type} />
            <span className={s.iterationInfo}>
              {t('project.detail.info.iteration', {
                stageLabel: <span className={s.orange}>{t(getStepLabel(project.currentStep as STEP, project.round))}</span>,
                current: <span className={s.orange}>{project.round}</span>,
              })}
            </span>
            <span>
              <span>{t('project.train_classes')}: </span>
              <span className={s.black}>{project?.keywords?.join(',')}</span>
            </span>
            {project.description ? (
              <span>
                {t('project.detail.desc')}: {project.description}
              </span>
            ) : null}
          </Space>
        </Col>
        <Col>{extra}</Col>
      </Row>
    </div>
  )
}
export default ProjectDetail
