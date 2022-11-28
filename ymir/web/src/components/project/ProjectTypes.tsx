import { Form } from 'antd'
import React from 'react'

import t from '@/utils/t'
import RadioGroup from '@/components/form/RadioGroup'
import { getProjectTypes, PROJECTTYPES } from '@/constants/project'

type Props = {
  label?: string
  name?: string
}

const options = getProjectTypes()
const ProjectTypes: React.FC<Props> = ({ label, name = 'type', ...rest }) => {
  return (
    <Form.Item name={name} label={t(label ? label : 'project.types.label')} initialValue={PROJECTTYPES.ObjectDetection}>
      <RadioGroup options={options} {...rest} />
    </Form.Item>
  )
}

export default ProjectTypes
