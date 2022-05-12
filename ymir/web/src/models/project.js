import {
  getProjects,
  getProject,
  delProject,
  createProject,
  updateProject,
  addExampleProject,
  checkStatus,
} from "@/services/project"
import { transferProject } from '@/constants/project'
import { deepClone } from '@/utils/object'

const initQuery = {
  name: "",
  offset: 0,
  limit: 20,
}
const initState = {
  query: initQuery,
  list: {
    items: [],
    total: 0,
  },
  projects: {},
}

export default {
  namespace: "project",
  state: deepClone(initState),
  effects: {
    *getProjects({ payload }, { call, put }) {
      const { code, result } = yield call(getProjects, payload)
      if (code === 0) {
        const projects = { items: result.items.map(project => transferProject(project)), total: result.total }
        yield put({
          type: "UPDATE_LIST",
          payload: projects,
        })
        return projects
      }
    },
    *getProject({ payload }, { select, call, put }) {
      const { id, force } = payload
      if (!force) {
        const cache = yield select(state => state.project.projects)
        const cacheProject = cache[id]
        if (cacheProject) {
          return cacheProject
        }
      }
      const { code, result } = yield call(getProject, id)
      if (code === 0) {
        const project = transferProject(result)
        yield put({
          type: "UPDATE_PROJECTS",
          payload: project,
        })
        return project
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
    *addExampleProject({ payload }, { call, put }) {
      const { code, result } = yield call(addExampleProject, payload)
      if (code === 0) {
        return result
      }
    },
    *updateProject({ payload }, { call, put }) {
      const { id, ...params } = payload
      const { code, result } = yield call(updateProject, id, params)
      if (code === 0) {
        yield put({
          type: 'clearCache'
        })
        return result
      }
    },
    *updateQuery({ payload = {} }, { put, select }) {
      const query = yield select(({ project }) => project.query)
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
    *clearCache({ }, { put }) {
      yield put({ type: 'CLEAR_ALL' })
    },
    *checkStatus({ payload }, { call, put }) {
      const pid = payload
      const { code, result } = yield call(checkStatus, pid)
      if (code === 0) {
        return result
      }
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
      const projects = { ...state.projects }
      const project = payload
      projects[project.id] = project
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
    CLEAR_ALL() {
      return deepClone(initState)
    },
  },
}
