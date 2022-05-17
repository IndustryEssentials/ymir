import { format } from '@/utils/date'
import {
  states,
  statesLabel,
  transferDatasetGroup,
  transferDataset,
} from '../dataset'

jest.mock('umi', () => {
  return {
    getLocale() {
      return 'zh-CN'
    },
  }
})

const createTime = "2022-03-10T03:39:09"
const task = {
  "name": "t00000020000013277a01646883549",
  "type": 105,
  "project_id": 1,
  "is_deleted": false,
  "create_datetime": createTime,
  "update_datetime": createTime,
  "id": 1,
  "hash": "t00000020000013277a01646883549",
  "state": 3,
  "error_code": null,
  "duration": 18,
  "percent": 1,
  "parameters": {},
  "config": {},
  "user_id": 2,
  "last_message_datetime": "2022-03-10T03:39:09.033206",
  "is_terminated": false,
  "result_type": null
}

const ds = id => ({
  "group_name": "dataset_training",
  "result_state": 1,
  "project_id": 234,
  "dataset_group_id": 1,
  state: 1,
  "keywords": { cat: 143, dog: 145 },
  "ignored_keywords": { person: 34 },
  negative_info: {},
  "asset_count": 234,
  "keyword_count": 2,
  'is_protected': false,
  "is_deleted": false,
  "create_datetime": createTime,
  "update_datetime": createTime,
  "id": id,
  "hash": "t00000020000012afef21646883528",
  "version_num": 1,
  "task_id": 1,
  "user_id": 2,
  "related_task": task,
})

describe("constants: dataset", () => {
  it("function -> statesLabel.", () => {
    expect(statesLabel(states.READY)).toBe('dataset.state.ready')
    expect(statesLabel(states.VALID)).toBe('dataset.state.valid')
    expect(statesLabel(states.INVALID)).toBe('dataset.state.invalid')

  })
  it('function -> transferDatasetGroup.', () => {
    const time = '2022-04-15T05:43:38'
    const origin = {
      id: 8345,
      project_id: 52334,
      name: 'dataset name',
      create_datetime: time,
    }
    const expected = {
      id: origin.id,
      projectId: origin.project_id,
      name: origin.name,
      createTime: format(time),
      versions: [],
    }
    expect(transferDatasetGroup(origin)).toEqual(expected)
  })
  it('function -> transferDataset.', () => {
    const id = 135234
    const dataset = ds(id)
    const expected = {
      id,
      groupId: 1,
      projectId: 234,
      name: 'dataset_training',
      version: 1,
      versionName: 'V1',
      assetCount: 234,
      keywords: ['cat', 'dog'],
      keywordCount: 2,
      keywordsCount: { cat: 143, dog: 145 },
      nagetiveCount: 0,
      isProtected: false,
      projectNagetiveCount: 0,
      ignoredKeywords: ['person'],
      hash: 't00000020000012afef21646883528',
      state: 1,
      hidden: true,
      createTime: format(createTime),
      updateTime: format(createTime),
      taskId: task.id,
      progress: task.percent,
      taskState: task.state,
      taskType: task.type,
      duration: 18,
      durationLabel: '1 分钟',
      taskName: task.name,
      task,
    }
    expect(transferDataset(dataset)).toEqual(expected)
  })
})
