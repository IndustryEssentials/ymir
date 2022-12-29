import { DatePicker } from "antd"
import { RangePickerProps } from "antd/lib/date-picker"
import moment from "moment"
import { FC } from "react"

const { RangePicker } = DatePicker

const Time: FC<RangePickerProps> = (props) => {

  return <RangePicker {...props} ranges={{
    ['Last 3 days']: [ moment().subtract(3, 'day'), moment()],
    ['Last 7 days']: [ moment().subtract(7, 'day'), moment()],
    ['Last 30 days']: [ moment().subtract(30, 'day'), moment()],
  }} />
}

export default Time
