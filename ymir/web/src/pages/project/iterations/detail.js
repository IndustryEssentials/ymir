import React, { useEffect, useState } from "react"

import t from "@/utils/t"

import s from "./index.less"

function Detail({ project }) {
  console.log('iteration detail => project:', project)

  return (
    <div className={s.list}>
         hello detail
    </div>
  )
}

export default Detail
