import { Space, Tag } from 'antd'
import { connect } from 'dva'
import { useEffect, useState } from 'react'

import t from "@/utils/t"
import s from './common.less'

const RecommandKeywords = ({sets = [], type = '', onSelected = () => {}, getRecommandKeywords}) => {
  const [keywords, setKeywords] = useState([])

  useEffect(() => {
    fetchKeywords()
  }, [])

  async function fetchKeywords() {
    const result = await getRecommandKeywords({ type })
    if (result) {
      setKeywords(result)
    }
  }

  return (
    <Space className={s.recommandKeywords}>
      <span className={s.label}>{t('common.recommand.keyword.label')}</span>
      {keywords.map(keyword => <Tag className={s.tag} key={keyword} onClick={() => onSelected(keyword)}>{keyword}</Tag>)}
    </Space>
  )
}

const props = (state) => {
  return {

  }
}

const actions = (dispatch) => {
  return {
    getRecommandKeywords(payload) {
      return dispatch({
        type: 'keyword/getRecommandKeywords',
        payload,
      })
    }
  }
}


export default connect(props, actions)(RecommandKeywords)