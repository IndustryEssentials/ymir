import React, { useCallback, useEffect, useState } from "react"
import { Card } from "antd"
import { useLocation, useParams, connect, useHistory } from "umi"

import Breadcrumbs from "@/components/common/breadcrumb"
import Detail from './components/detail'
import Models from '@/components/model/list'

import s from "./detail.less"

function ProjectDetail(func) {
  const history = useHistory()
  const location = useLocation()
  const { id } = useParams()
  const [iterations, setIterations] = useState([])
  const [group, setGroup] = useState(0)
  const [project, setProject] = useState({})

  useEffect(() => {
    id && fetchProject(true)
    id && fetchIterations(id)
  }, [id])

  useEffect(() => {
    const locationHash = location.hash.replace(/^#/, '')
    const [tabKey, gid] = (locationHash || '').split('_')
    setGroup(gid)
  }, [location.hash])

  async function fetchProject(force) {
    const result = await func.getProject(id, force)
    if (result) {
      setProject(result)
    }
  }
  const fresh = useCallback(() => {
    fetchProject(true)
  }, [])

  async function fetchIterations(pid) {
    const iterations = await func.getIterations(pid)
    if (iterations) {
      setIterations(iterations)
    }
  }

  return (
    <div className={s.projectDetail}>
      <Breadcrumbs />
      <div className={s.header}>
        <Detail project={project} iterations={iterations} fresh={fresh} />
      </div>
      <Card className='noShadow'
        style={{ margin: '10px -20px 0', background: 'transparent' }}
        bodyStyle={{ padding: '0 20px' }}
      >
        <Models pid={id} project={project} group={group} iterations={iterations} />
      </Card>
    </div>
  )
}


const actions = (dispatch) => {
  return {
    getProject(id, force) {
      return dispatch({
        type: 'project/getProject',
        payload: { id, force },
      })
    },
    getIterations(id) {
      return dispatch({
        type: 'iteration/getIterations',
        payload: { id, },
      })
    },
  }
}

export default connect(null, actions)(ProjectDetail)
