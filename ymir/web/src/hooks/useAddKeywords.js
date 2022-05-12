import { useState } from 'react'
import { useDispatch } from 'umi'

const useAddKeywords = (dry_run = false) => {
  const dispatch = useDispatch()
  const updateKeywords = keywords => dispatch({
    type: 'keyword/updateKeywords',
    payload: {
      keywords: keywords.map(k => ({ name: k })), dry_run,
    }
  })
  const [repeated, setRepeated] = useState([])
  const [newer, setNewer] = useState([])

  const add = async (keywords) => {
    keywords = [...new Set(keywords)]
    if (!keywords.length) {
      return
    }
    const result = await updateKeywords(keywords)
    if (result?.failed) {
      setRepeated(result?.failed)
      setNewer(keywords.filter(kw => !result.failed.includes(kw)))
    }
    return result
  }

  return [{ repeated, newer }, add]
}

export default useAddKeywords
