import { Cascader, Col, Row, Select } from 'antd'
import { connect } from 'dva'
import { useEffect, useState } from 'react'


const ProjectSelect = ({ pid, value, projects = [], onChange = () => { }, getProjects, getModels, ...resProps }) => {
  const [options, setOptions] = useState([])

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
    getModels(pid) {
      return dispatch({
        type: 'model/queryAllModels',
        payload: pid,
      })
    }
  }
}
export default connect(props, actions)(ProjectSelect)
