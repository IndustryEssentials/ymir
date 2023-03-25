import React, { FC, ReactNode } from 'react'
import { Button, Col, Row, Space } from 'antd'
import { Link, useSelector } from 'umi'

import t from '@/utils/t'
import { getStepLabel, STEP } from '@/constants/iteration'
import useFetch from '@/hooks/useFetch'
import { getProjectTypeLabel } from '@/constants/project'

import ObjectTypeTag from '@/components/project/ObjectTypeTag'

import s from '../detail.less'
import { EditIcon, SearchEyeIcon, EyeOffIcon } from '@/components/common/Icons'
import { ArrowDownIcon, ArrowRightIcon } from '@/components/common/Icons'

const ProjectDetail: FC<{ project: YModels.Project, extra?: ReactNode }> = ({ project, extra }) => {
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
        <Col>
          {extra}
        </Col>
      </Row>
    </div>
  )
}
export default ProjectDetail
