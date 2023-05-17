import useRequest from '@/hooks/useRequest'
import { Cascader, CascaderProps } from 'antd'
import { ValueType, DefaultOptionType } from 'rc-cascader/lib/Cascader'
import { FC, useEffect, useState } from 'react'
import { useSelector } from 'react-redux'

interface OptionType extends DefaultOptionType {
  loading?: boolean,
}

type Props = CascaderProps<OptionType> & {
  pid: number,
  type: number,
  onChange: (value: ValueType, option: DefaultOptionType[] | DefaultOptionType[][]) => void
}

const ProjectModelSelect: FC<Props> = ({ pid, type, value, onChange, ...resProps }) => {
  const [options, setOptions] = useState<OptionType[]>([])
  const projects = useSelector<YStates.Root, YModels.Project[]>(({ project }) => project.list.items)
  const {runAsync: getProjects } = useRequest<YModels.Project[], any[]>('project/getProjects', {
    debounceWait: 300,
    loading: false,
  })
  const { runAsync: getModels} = useRequest<YModels.Model[], any[]>('model/queryAllModels', {
    loading: false,
  })

  useEffect(() => {
    type && fetchProjects()
  }, [type])

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
      value = [projects[0].id]
    }
  }, [projects])

  function fetchProjects() {
    getProjects({ limit: 10000, type })
  }

  async function loadData(selected: OptionType[]) {
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

  const change = (value: ValueType, option: DefaultOptionType[] | DefaultOptionType[][]) => onChange && onChange(value, option)

  return (
    <Cascader {...resProps}  value={value} options={options} loadData={(selected) => loadData(selected)} onChange={change} allowClear></Cascader>
  )
}

export default ProjectModelSelect
