import { FC } from "react"
import { DatePicker } from "antd"
import { RangePickerProps } from "antd/lib/date-picker"
import moment from "moment"

import t from '@/utils/t'

const { RangePicker } = DatePicker

const Time: FC<RangePickerProps> = (props) => {

  return <RangePicker {...props} ranges={{
    [t('date.range.today')]: [ moment(), moment()],
    [t('date.range.last3days')]: [ moment().subtract(2, 'day'), moment()],
    [t('date.range.last7days')]: [ moment().subtract(6, 'day'), moment()],
  }} />
}

export default Time
