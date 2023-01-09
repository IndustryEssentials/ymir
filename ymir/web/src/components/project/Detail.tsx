import { FC } from 'react'
import { Button, Space } from 'antd'
import t from '@/utils/t'
import s from './detail.less'
import TestingSet from './TestingSet'
import { useHistory } from 'umi'

type Props = {
  project?: YModels.Project
  back?: boolean
}

const Detail: FC<Props> = ({ project, back }) => {
  const history = useHistory()
  const backBtn = <Button className={s.back} onClick={() => history.goBack()}>{t('common.back')}</Button>
  return project ? (
    <div className={s.header}>
      <Space className={s.detailPanel} wrap size={16}>
        <span className={s.name}>{project.name}</span>
        <span className={s.type}>
          {t('project.types.label')}: {t(project.typeLabel)}
        </span>
        <span>
          {t('project.train_classes')}: <span className={s.black}>{project?.keywords?.join(',')}</span>
        </span>
        {project.description ? (
          <span>
            {t('project.detail.desc')}: {project.description}
          </span>
        ) : null}
      </Space>
      {back ? backBtn : null}
      <TestingSet project={project} />
    </div>
  ) : null
}

export default Detail
