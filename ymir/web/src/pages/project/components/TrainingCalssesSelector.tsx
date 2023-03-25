import { FC, useEffect, useState } from 'react'
import { Col, Row, Select, SelectProps } from 'antd'
import t from '@/utils/t'
import { useSelector } from 'umi'
import useRequest from '@/hooks/useRequest'

type Props = SelectProps & {
  pid: number
}
const TrainingClassesSelector: FC<Props> = ({ pid, onChange, ...props }) => {
  const [classes, setClasses] = useState<string[]>([])
  const project = useSelector(({ project }) => project.projects[pid])
  const trainingDataset = useSelector(({ dataset }) => dataset.dataset[project?.candidateTrainSet])
  const model = useSelector(({ model }) => project?.model && model.model[project.model])
  const { data: updateResult, run: updateTrainClasses } = useRequest<Object, [{ id: number; classes: string[] }]>('iteration/updateTrainClasses')

  useEffect(() => {
    if (trainingDataset) {
      setClasses(trainingDataset.keywords)
    } else if (model) {
      setClasses(model.keywords)
    }
  }, [trainingDataset, model])

  return (
    <Select
      showArrow
      placeholder={t('project.add.form.keyword.placeholder')}
      style={{ minWidth: 120 }}
      {...props}
      options={classes.map((cs) => ({ value: cs, label: cs }))}
      onChange={(value: string[], option) => {
        console.log('value:', value)
        updateTrainClasses({ id: pid, classes: value })
        onChange && onChange(value, option)
      }}
      mode="multiple"
    ></Select>
  )
}

export default TrainingClassesSelector
