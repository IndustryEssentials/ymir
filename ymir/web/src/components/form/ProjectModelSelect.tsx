import useRequest from '@/hooks/useRequest'
import { Cascader, CascaderProps, CheckboxOptionType, Col, Row, Select } from 'antd'
import { FC, useEffect, useState } from 'react'

type Props = CascaderProps<CheckboxOptionType> & {
  pid: number,
  type: number,
}

const ProjectModelSelect: FC<Props> = ({ pid, type, value, onChange, ...resProps }) => {
  const [options, setOptions] = useState<CheckboxOptionType[]>([])
  const { data: projects = [], run: getProjects } = useRequest<YModels.Project[], []>('project/getProject', {
    debounceWait: 300,
    loading: false,
  })
  const { data: models, run: getModels} = useRequest('model/getModels', {
    loading: false,
  })

  useEffect(() => {
    fetchProjects()
  }, [])

  useEffect(() => {
    const opts = projects.filter(project => project.id !== Number(pid)).map(project => {
      return {
        label: project.name,
        value: project.id,
        isLeaf: false,
      }
    })
    setOptions(opts)
  }, [projects])

  useEffect(() => {
    if (projects.length === 1) {
      value = projects[0].id
    }
  }, [projects])

  function fetchProjects() {
    getProjects()
  }

  async function loadData(selected) {
    const target = selected[selected.length - 1]
    target.loading = true
    const result = await getModels(target.value)
    
    target.loading = false
    if (result) {
      target.children = result.map(model => {
        return {
          label: model.name + model.versionName,
          value: model.id,
          isLeaf: true,
        }
      }) || []
      setOptions([...options])
    }
  }

  return (
    <Cascader {...resProps}  value={value} options={options}loadData={loadData} onChange={onChange} allowClear></Cascader>
  )
}

export default ProjectModelSelect
