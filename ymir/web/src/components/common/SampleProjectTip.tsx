import { FC, useEffect } from 'react'
import { message } from 'antd'
import { useSelector } from 'umi'
import useRequest from '@/hooks/useRequest'
import t from '@/utils/t'

const key = 'sampleProject'
const SampleProjectTip: FC<{ id?: number }> = ({ id }) => {
  const project = useSelector(({ project }) => (id ? project.projects[id] : undefined))
  const { run: getProject } = useRequest('project/getProject', {
    loadingDelay: 1000,
  })

  useEffect(() => {
    id && getProject({ id })
  }, [id])

  useEffect(() => {
    if (project?.recommendImage) {
      message.open({
        key,
        type: 'warning',
        content: t('project.example.tip'),
        duration: 0,
      })
    } else {
      message.destroy(key)
    }
  }, [project])
  return <></>
}

export default SampleProjectTip
