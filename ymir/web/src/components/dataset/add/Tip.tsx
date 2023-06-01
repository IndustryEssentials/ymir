import { FC, useState, useEffect } from 'react'
import { Button } from 'antd'
import { useParams, useSelector } from 'umi'
import t from '@/utils/t'
import { getTypeLabel, Types } from './AddTypes'
import { isDetection, ObjectType } from '@/constants/objectType'
import DetSamplePic from '@/assets/sample.png'
import SegSamplePic from '@/assets/sample_seg.png'
import useRequest from '@/hooks/useRequest'
import { Project } from '@/constants'
type Props = {
  type: Types
}

const Tip: FC<Props> = ({ type }) => {
  const { id } = useParams<{ id: string }>()
  const [sampleZip, setSampleZip] = useState('/sample_dataset.zip')
  const [samplePic, setSamplePic] = useState(DetSamplePic)
  const project = useSelector(({ project }) => project.projects[id])
  const structureTip = t('dataset.add.form.tip.structure', {
    br: <br />,
    pic: <img src={samplePic} />,
    detail: <Button onClick={() => showFormatDetail(true)}>{t('dataset.add.form.tip.format.detail')}</Button>,
  })
  const label = getTypeLabel(type, false)
  const [config, setConfig] = useState<{ [key: string]: any }>({
    br: <br />,
    structure: '',
    format: 'Coco',
    sample: '',
  })
  const { run: showFormatDetail } = useRequest<null, [boolean]>('dataset/showFormatDetail', { loading: false })
  const { run: getProject } = useRequest<Project, [{ id: string }]>('project/getProject', {
    cacheKey: 'getProject',
    loading: false,
  })

  useEffect(() => {
    id && getProject({ id })
  }, [id])
  useEffect(() => {
    console.log('project:', project, isDetection(project?.type))
    !isDetection(project?.type) && (setSamplePic(SegSamplePic), setSampleZip('/sample_dataset_seg.zip'))
  }, [project?.type])

  useEffect(() => {
    const structureTip = t('dataset.add.form.tip.structure', {
      br: <br />,
      pic: <img src={samplePic} />,
      detail: <Button onClick={() => showFormatDetail(true)}>{t('dataset.add.form.tip.format.detail')}</Button>,
    })
    const conf = {
      ...config,
      structure: structureTip,
      // sample: (
      //   <a target="_blank" href={sampleZip}>
      //     Sample.zip
      //   </a>
      // ),
      format: isDetection(project?.type) ? 'Pascal VOC' : 'Coco',
    }
    if (type === Types.LOCAL) {
      setConfig({
        ...conf,
        sample: (
          <a target="_blank" href={sampleZip}>
            Sample.zip
          </a>
        ),
      })
    } else {
      setConfig(conf)
    }
  }, [type, project, samplePic, sampleZip])

  return <>{t(`dataset.add.form.${label}.tip`, config)}</>
}
export default Tip
