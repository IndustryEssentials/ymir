import { Message } from '@/constants'
import { transferMessage } from '@/constants/message'
import { TaskResultType } from '@/constants/TaskResultType'
import { getMessages as queryMessages, getMessage, readMessage as readMsg } from '@/services/message'
import { QueryParams } from '@/services/typings/message'
import { MessageState, MessageStore } from '.'
import { Effect } from './typings/common'
import { createEffect, createReducers } from './_utils'

const state: MessageState = {
  messages: [],
  total: 0,
  fresh: false,
  latest: undefined,
}

const reducers = createReducers<MessageState>([
  { name: 'UpdateMessages', field: 'messages' },
  { name: 'UpdateTotal', field: 'total' },
  { name: 'UpdateFresh', field: 'fresh' },
  { name: 'UpdateLatest', field: 'latest' },
])

const getMessages: Effect<QueryParams & { simple?: boolean }> = createEffect(function* ({ payload }, { call, put }) {
  const { simple, ...params } = payload
  const { code, result } = yield call(queryMessages, params)
  if (code === 0) {
    const { items, total } = result
    const messages: Message[] = items.map(transferMessage)
    yield put({ type: 'UpdateMessages', payload: messages })
    yield put({ type: 'UpdateTotal', payload: total })
    yield put({ type: 'UpdateFresh', payload: false })
    if (!simple) {
      const list: Message[] = yield put.resolve({ type: 'getRelatedSource', payload: messages })
      if (list?.length) {
        yield put({ type: 'UpdateMessages', payload: list })
      }
    }
    return messages
  }
})

const getRelatedSource: Effect = createEffect<Message[]>(function* ({ payload: messages }, { put }) {
  const ids = messages.reduce<{ [key: string]: number[] }>((prev, curr) => {
    prev[curr.resultModule] = prev[curr.resultModule] ? [...prev[curr.resultModule], curr.resultId] : [curr.resultId]
    return prev
  }, {})
  for (const module in ids) {
    const resultIds = ids[module]
    if (module) {
      const list: Message['result'][] = yield put.resolve({
        type: `${module}/batch`,
        payload: resultIds,
      })
      messages.forEach((item, ind) => {
        const index = list?.findIndex((result) => result?.id === item.resultId)
        if (index >= 0) {
          messages[ind].result = list[index]
        }
      })
    }
    return messages
  }
})

const readMessage: Effect<number> = createEffect(function* ({ payload: id }, { call, put, select }) {
  const { code, result } = yield call(readMsg, id)
  if (code === 0) {
    const { latest, messages }: MessageState = yield select(({ message }) => message)
    if (messages.some((msg) => msg.id === id)) {
      yield put({ type: 'getMessages', payload: {} })
    }
    if (latest?.id === id) {
      yield put.resolve({ type: 'UpdateLatest', payload: null })
    }
    return result
  }
})

const asyncMessages: Effect<{}> = createEffect(function* ({ payload: originalData }, { put, select }) {
  const message = transferMessage(originalData)
  const { total } = yield select(({ message }) => message)
  yield put({ type: 'UpdateTotal', payload: total + 1 })
  yield put({ type: 'UpdateFresh', payload: true })
  const msgs = yield put.resolve({ type: 'getRelatedSource', payload: [message] })
  yield put({ type: 'UpdateLatest', payload: msgs[0] })
})

const getUnreadCount: Effect = createEffect(function* ({ payload }, { call, put }) {
  yield put({
    type: 'getMessages',
    payload: {
      simple: true,
      is_read: false,
    },
  })
})

const MessageModel: MessageStore = {
  namespace: 'message',
  state,
  effects: {
    getMessages,
    asyncMessages,
    getUnreadCount,
    readMessage,
    getRelatedSource,
  },
  reducers,
}

export default MessageModel
