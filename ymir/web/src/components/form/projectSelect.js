import { Col, Row, Select } from 'antd'
import { connect } from 'dva'
import { useEffect, useState } from 'react'

import { percent } from '@/utils/number'


const ProjectSelect = ({ pid, value, allProjects, onChange = () => { }, getProjects, ...resProps }) => {
  const [options, setOptions] = useState([])
  const [projects, setProjects] = useState([])

  useEffect(() => {
    fetchProjects()
  }, [])

  useEffect(() => {
    setProjects(allProjects)
  }, [allProjects])

  useEffect(() => {
    if (options.length === 1) {
      value = options[0].value
    }
  }, [options])

  useEffect(() => {
    generateOptions()
  }, [projects])

  function fetchProjects() {
    getProjects(pid)
  }

  function generateOptions() {
    const opts = projects.map(project => {
      return {
        label: <Row gutter={10} wrap={false}>
          <Col flex={1}>{project.name} {project.versionName}</Col>
          <Col>mAP: <strong title={project.map}>{percent(project.map)}</strong></Col>
        </Row>,
        project,
        value: project.id,
      }
    })
    setOptions(opts)
  }

  return (
    <Select value={value} {...resProps} onChange={(value, option) => onChange(value, option?.project)} options={options} allowClear></Select>
  )
}

const props = (state) => {
  return {
    allProjects: state.project.allProjects,
  }
}
const actions = (dispatch) => {
  return {
    getProjects(pid) {
      return dispatch({
        type: 'project/queryAllProjects',
        payload: pid,
      })
    }
  }
}
export default connect(props, actions)(ProjectSelect)
