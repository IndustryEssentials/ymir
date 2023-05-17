import { FC, useEffect } from 'react'
import { Button, Col, Row, Space } from 'antd'
import t from '@/utils/t'
import s from './detail.less'
import TestingSet from './TestingSet'
import { useHistory, useSelector } from 'umi'
import ObjectTypeTag from './ObjectTypeTag'
import Stats from './Stats'
import useRequest from '@/hooks/useRequest'
import { Project } from '@/constants'

type Props = {
  pid: number
  project?: Project
  type?: 'dataset' | 'model'
  back?: boolean
}

const Detail: FC<Props> = ({ pid, type, back }) => {
  const history = useHistory()
  const project = useSelector(({ project }) => project.projects[pid])
  const tasks = useSelector(({ socket }) => socket.tasks)
  const { run: getProject } = useRequest<null, [{ id: number; force?: boolean }]>('project/getProject', { loading: false, loadingDelay: 500 })

  useEffect(() => {
    pid && getProject({ id: pid })
  }, [pid])

  useEffect(() => {
    const needUpdate = tasks.some((task) => task.reload)
    if (needUpdate) {
      getProject({ id: pid, force: true })
    }
  }, [tasks])

  const backBtn = (
    <Button className={s.back} onClick={() => history.goBack()}>
      {t('common.back')}
    </Button>
  )
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
        <Col span={12} style={{ borderLeft: '1px solid #d2def2' }}>
          {type ? <Stats project={project} type={type} /> : back ? backBtn : null}
        </Col>
      </Row>
      <TestingSet project={project} />
    </div>
  ) : null
}

export default Detail
