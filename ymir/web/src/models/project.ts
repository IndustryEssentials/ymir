import { getProjects, getProject, delProject, createProject, updateProject, addExampleProject, checkStatus } from '@/services/project'
import { transferProject } from '@/constants/project'
import { deepClone } from '@/utils/object'
import { createEffect, createReducersByState } from './_utils'
import { ProjectState, ProjectStore } from '.'
import { List } from './typings/common'
import { Project } from '@/constants'

const initQuery = {
  name: '',
  current: 1,
  offset: 0,
  limit: 20,
}
const initState: ProjectState = {
  query: initQuery,
  list: {
    items: [],
    total: 0,
  },
  projects: {},
  current: undefined,
}

const ProjectModel: ProjectStore = {
  namespace: 'project',
  state: deepClone(initState),
  effects: {
    getProjects: createEffect(function* ({ payload }, { call, put }) {
      const { code, result } = yield call(getProjects, payload)
      if (code === 0) {
        const projects: List<Project> = { items: result.items.map(transferProject), total: result.total }
        yield put({
          type: 'UpdateList',
          payload: projects,
        })
        return projects
      }
    }),
    getProject: createEffect(function* ({ payload }, { select, call, put }) {
      const { id, force } = payload
      if (!force) {
        const cache = yield select((state) => state.project.projects)
        const cacheProject = cache[id]
        if (cacheProject) {
          yield put({
            type: 'UpdateCurrent',
            payload: cacheProject,
          })
          return cacheProject
        }
      }
      const { code, result } = yield call(getProject, id)
      if (code === 0) {
        const project = transferProject(result)
        yield put({
          type: 'UpdateProjects',
          payload: { [project.id]: project },
        })
        yield put({
          type: 'UpdateCurrent',
          payload: project,
        })
        return project
      }
    }),
    delProject: createEffect(function* ({ payload }, { call, put }) {
      const { code, result } = yield call(delProject, payload)
      if (code === 0) {
        return result
      }
    }),
    createProject: createEffect(function* ({ payload }, { call, put }) {
      const { code, result } = yield call(createProject, payload)
      if (code === 0) {
        const project = transferProject(result)
        yield put({
          type: 'UpdateProjects',
          payload: { [project.id]: project },
        })
        return project
      }
    }),
    addExampleProject: createEffect(function* ({ payload }, { call, put }) {
      const { code, result } = yield call(addExampleProject, payload)
      if (code === 0) {
        return result
      }
    }),
    updateProject: createEffect(function* ({ payload }, { call, put }) {
      const { id, ...params } = payload
      const { code, result } = yield call(updateProject, id, params)
      if (code === 0) {
        const project = transferProject(result)
        yield put({
          type: 'UpdateProjects',
          payload: { [project.id]: project },
        })
        return project
      }
    }),
    updateQuery: createEffect(function* ({ payload = {} }, { put, select }) {
      const query = yield select(({ project }) => project.query)
      yield put({
        type: 'UpdateQuery',
        payload: {
          ...query,
          ...payload,
          offset: query.offset === payload.offset ? initQuery.offset : payload.offset,
        },
      })
    }),
    resetQuery: createEffect(function* ({}, { put }) {
      yield put({
        type: 'UpdateQuery',
        payload: initQuery,
      })
    }),
    clearCache: createEffect(function* ({}, { put }) {
      yield put({ type: 'CLEAR_ALL' })
    }),
    checkStatus: createEffect(function* ({ payload }, { call, put }) {
      const pid = payload
      const { code, result } = yield call(checkStatus, pid)
      if (code === 0) {
        return result
      }
    }),
  },
  reducers: {
    ...createReducersByState(initState),
    UPDATE_PREPARETRAINSET(state, { payload }) {
      return {
        ...state,
        prepareTrainSet: payload,
      }
    },
    CLEAR_ALL() {
      return deepClone(initState)
    },
  },
}

export default ProjectModel
