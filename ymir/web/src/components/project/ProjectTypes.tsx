import { Form, RadioGroupProps } from 'antd'
import React from 'react'

import t from '@/utils/t'
import RadioGroup from '@/components/form/RadioGroup'
import { getProjectTypes, ObjectType } from '@/constants/project'

type Props = RadioGroupProps & {
  label?: string
  name?: string
}

const options = getProjectTypes()
const ProjectTypes: React.FC<Props> = ({ label, name = 'type', ...rest }) => {
  return (
    <Form.Item required name={name} label={t(label ? label : 'project.types.label')} initialValue={ObjectType.ObjectDetection}>
      <RadioGroup {...rest} options={options} />
    </Form.Item>
  )
}

export default ProjectTypes
