import { Cascader, CascaderProps } from 'antd'
import { FC, ReactNode, useEffect, useState } from 'react'

import DatasetOption from '@/components/form/option/Dataset'
import { useSelector } from 'umi'
import { Dataset } from '@/constants'
import useRequest from '@/hooks/useRequest'
type DataNodeType = {
  label: ReactNode
  value: number
  dataset?: Dataset
  isLeaf?: boolean
  loading?: boolean
  children?: DataNodeType[]
}
type Props = CascaderProps<DataNodeType> & {}

const ProjectDatasetSelect: FC<Props> = (props) => {
  const [options, setOptions] = useState<DataNodeType[]>([])
  const projects = useSelector(({ project }) => project.list.items)
  const { run: getProjects } = useRequest('project/getProjects', { cacheKey: 'getAllProjects', loading: false })
  const { runAsync: getDatasets } = useRequest<Dataset[], [{ id: number; force?: boolean }]>('project/queryAllDatasets', {
    cacheKey: 'getAllDatasets',
    loading: false,
  })

  useEffect(() => {
    fetchProjects()
  }, [])

  useEffect(() => {
    const opts = projects.map((project) => {
      return {
        label: project.name,
        value: project.id,
        isLeaf: false,
      }
    })
    setOptions(opts)
  }, [projects])

  function fetchProjects() {
    getProjects()
  }

  const loadData: Props['loadData'] = async (selected) => {
    const target = selected[selected.length - 1]
    if (!target.value) {
      return
    }
    target.loading = true
    const result = await getDatasets({ id: Number(target.value), force: true })

    target.loading = false
    if (result) {
      target.children =
        result.map((dataset) => {
          return {
            label: <DatasetOption dataset={dataset} />,
            value: dataset.id,
            dataset: dataset,
            isLeaf: true,
          }
        }) || []
      setOptions([...options])
    }
  }

  return <Cascader allowClear {...props} options={options} loadData={loadData}></Cascader>
}

export default ProjectDatasetSelect
