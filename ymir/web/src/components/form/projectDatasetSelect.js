import { Cascader, Col, Row, Select } from 'antd'
import { connect } from 'dva'
import { useEffect, useState } from 'react'


const ProjectDatasetSelect = ({ pid, value, projects = [], onChange = () => { }, getProjects, getDatasets, ...resProps }) => {
  const [options, setOptions] = useState([])

  useEffect(() => {
    fetchProjects()
  }, [])

  useEffect(() => {
    const opts = projects.map(project => {
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
    const result = await getDatasets(target.value, true)
    
    target.loading = false
    if (result) {
      target.children = result.map(dataset => {
        return {
          label: `${dataset.name} ${dataset.versionName} (assets: ${dataset.assetCount})`,
          value: dataset.id,
          isLeaf: true,
        }
      }) || []
      setOptions([...options])
    }
  }

  return (
    <Cascader value={value} options={options} {...resProps} loadData={loadData} onChange={onChange} allowClear></Cascader>
  )
}

const props = (state) => {
  return {
    projects: state.project.list.items,
  }
}
const actions = (dispatch) => {
  return {
    getProjects() {
      return dispatch({
        type: 'project/getProjects',
        payload: { limit: 10000 },
      })
    },
    getDatasets(pid, force) {
      return dispatch({
        type: 'dataset/queryAllDatasets',
        payload: { pid, force },
      })
    }
  }
}
export default connect(props, actions)(ProjectDatasetSelect)
