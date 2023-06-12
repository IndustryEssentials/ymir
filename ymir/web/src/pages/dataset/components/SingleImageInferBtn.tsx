import { FC, useState, useEffect } from 'react'
import { useHistory, useParams, useSelector } from 'umi'
import t from '@/utils/t'
import { isMultiModal } from '@/constants/objectType'
import { Button, ButtonProps } from 'antd'
import useRequest from '@/hooks/useRequest'
type Props = ButtonProps & {
  url?: string
}
const SingleImageInferBtn: FC<Props> = ({ url, ...props }) => {
  const history = useHistory()
  const { id: pid } = useParams<{ id: string }>()
  const project = useSelector(({ project }) => project.projects[pid])
  const { run: getProject } = useRequest<null, [{ id: string | number }]>('project/getProject', {
    cacheKey: 'getCurrentProject',
    loading: false,
  })

  useEffect(() => {
    getProject({ id: pid })
  }, [])
  useEffect(() => {}, [])
  return (
    <Button
      type="primary"
      {...props}
      hidden={!isMultiModal(project?.type) || !url}
      onClick={() => history.push(`/home/project/${pid}/llmm/inference`, { url })}
    >
      {t('llmm.external.infer')}
    </Button>
  )
}
export default SingleImageInferBtn
