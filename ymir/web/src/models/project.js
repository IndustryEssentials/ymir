import {
  getProjects,
  getProject,
  getInterations,
  delProject,
  createProject,
  updateProject,
} from "@/services/project"
import { transferProject, tranferInteration } from '@/constants/project'

const initQuery = {
  name: "",
  offset: 0,
  limit: 20,
}

export default {
  namespace: "project",
  state: {
    query: initQuery,
    list: {
      items: [],
      total: 0,
    },
    projects: {},
  },
  effects: {
    *getProjects({ payload }, { call, put }) {
      const { code, result } = yield call(getProjects, payload)
      if (code === 0) {
        const projects = { items: result.items.map(project => transferProject(project)), total: result.total }
        yield put({
          type: "UPDATE_LIST",
          payload: projects,
        })
        return result
      }
    },
    *getProject({ payload }, { call, put }) {
      const { code, result } = yield call(getProject, payload)
      if (code === 0) {
        const project = transferProject(result)
        yield put({
          type: "UPDATE_PROJECT",
          payload: project,
        })
        return result
      }
    },
    *getInterations({ payload }, { call, put }) {
      const projectId = payload
      const { code, result } = yield call(getInterations, projectId)
      if (code === 0) {
        const interations = tranferInteration()
        yield put({
          type: "UPDATE_INTERATIONS",
          payload: { id: projectId, interations },
        })
        return result
      }
    },
    *delProject({ payload }, { call, put }) {
      const { code, result } = yield call(delProject, payload)
      if (code === 0) {
        return result
      }
    },
    *createProject({ payload }, { call, put }) {
      const { code, result } = yield call(createProject, payload)
      if (code === 0) {
        return result
      }
    },
    *updateProject({ payload }, { call, put }) {
      const { id, name } = payload
      const { code, result } = yield call(updateProject, id, name)
      if (code === 0) {
        return result
      }
    },
    *updateQuery({ payload = {} }, { put, select }) {
      const query = yield select(({ task }) => task.query)
      yield put({
        type: 'UPDATE_QUERY',
        payload: {
          ...query,
          ...payload,
          offset: query.offset === payload.offset ? initQuery.offset : payload.offset,
        }
      })
    },
    *resetQuery({ }, { put }) {
      yield put({
        type: 'UPDATE_QUERY',
        payload: initQuery,
      })
    },
  },
  reducers: {
    UPDATE_LIST(state, { payload }) {
      return {
        ...state,
        list: payload
      }
    },
    UPDATE_PROJECTS(state, { payload }) {
      const projects = { ...state.project }
      const project = payload
      projects[project.id] = project
      return {
        ...state,
        projects,
      }
    },
    UPDATE_INTERATIONS(state, { payload }) {
      const projects = { ...state.projects }
      const project = projects[id]
      const { id, interations } = payload
      project = {
        ...project,
        interations,
      }
      projects[id] = project
      return {
        ...state,
        projects,
      }
    },
    UPDATE_QUERY(state, { payload }) {
      return {
        ...state,
        query: payload,
      }
    },
  },
}
