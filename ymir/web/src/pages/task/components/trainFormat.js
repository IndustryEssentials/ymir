import { Radio } from "antd"

const annotationFormats = ['ark', 'voc', 'ls_json']
const assetFormats = ['raw', 'lmdb']

const TrainFormat = ({ value, onChange }) => {

  return <Radio.Group value={value} onChange={onChange}>
    {assetFormats.map(as => <p>{annotationFormats.map(an => <Radio value={`${an}:${as}`}>{as}/{an}</Radio>)}</p>)}
  </Radio.Group>
}

export default TrainFormat
