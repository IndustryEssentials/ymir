import trans from './trans'
import task from "./modules/task"
import dataset from "./modules/dataset"
import errors from "./modules/errors"
import login from "./modules/login"
import model from "./modules/model"
import routeTitle from "./modules/routeTitle"
import signup from "./modules/signup"
import common from "./modules/common"
import breadcrumbs from "./modules/breadcrumbs"
import portal from "./modules/portal"
import keyword from './modules/keyword'
import user from './modules/user'
import mirror from './modules/mirror'

const lang = {
  ...common,
  ...routeTitle,
  ...breadcrumbs,
  ...portal,
  ...login,
  ...signup,
  ...dataset,
  ...model,
  ...task,
  ...errors,
  ...keyword,
  ...user,
  ...mirror,
}
export default trans(lang, 'en')
