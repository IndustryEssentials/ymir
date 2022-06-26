import request from "@/utils/request"

/**
 * @param {*} params
 * { name, offset = 0, limit = 10 }
 * @returns
 */
/**
 * get datasets
 * @param {object} param1 {
 *   {string}   [name]        model name
 *   {number}   [offset]      query start
 *   {number}   [limit]       query count 
 *   {boolean}  [is_desc]     default as true
 *   {string}   [order_by]    value as: id, create_datetime, default as id
 * }
 * @returns 
 */
export function getVisualizations({ name, offset = 0, limit = 10, is_desc = true, order_by}) {
  return request.get("visualizations/", { params: { name, offset, limit, is_desc, order_by } })
}

/**
 * delete visualization
 * @param {number} id
 * @returns
 */
export function delVisualization(id) {
  return request({
    method: "delete",
    url: `/visualizations/${id}`,
  })
}

/**
 * create a visualization
 * @param {object} visualization
 * {
 *   {array<string>}  taskIds
 * }
 * @returns
 */
export function createVisualization({
  taskIds,
}) {
  return request.post("/visualizations/", {
    task_ids: taskIds
  })
}