import { Select } from 'antd'
import { connect } from 'dva'
import { useEffect, useState } from 'react'


const ModelSelect = ({ value, onChange = () => {}, getModels, ...resProps }) => {
  const [options, setOptions] = useState([])

  useEffect(() => {
    fetchModels()
  }, [])

  useEffect(() => {
    if (options.length === 1) {
      value = options[0].value
    }
  }, [options])

  async function fetchModels() {
    const params = {
      offset: 0,
      limit: 100000,
    }
    const result = await getModels(params)
    if (result) {
      const models = result.items
      const opts = models.map(model => {
        return {
          label: model.name,
          model,
          value: model.id,
        }
      })
      setOptions(opts)
      if (value) {
        const opt = opts.find(opt => opt.value === value)
        onChange(opt.value, opt.model)
      }
    }
  }

  return (
    <Select value={value} {...resProps} onChange={(value, { model }) => onChange(value, model)} options={options}></Select>
  )
}

const actions = (dispatch) => {
  return {
    getModels(payload) {
      return dispatch({
        type: 'model/getModels',
        payload,
      })
    }
  }
}
export default connect(null, actions)(ModelSelect)
