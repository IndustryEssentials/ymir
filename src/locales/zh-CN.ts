import trans from './trans'
import common from "./modules/common"
import dataset from "./modules/dataset"
import errors from "./modules/errors"
import forget from "./modules/forget"
import login from "./modules/login"
import model from "./modules/model"
import modify_pwd from "./modules/modify_pwd"
import reset_pwd from "./modules/reset_pwd"
import routeTitle from "./modules/routeTitle"
import signup from "./modules/signup"
import task from "./modules/task"
import breadcrumbs from "./modules/breadcrumbs"
import portal from "./modules/portal"
import keyword from './modules/keyword'

const lang = {
  ...common,
  ...routeTitle,
  ...breadcrumbs,
  ...portal,
  ...login,
  ...signup,
  ...forget,
  ...reset_pwd,
  ...modify_pwd,
  ...dataset,
  ...model,
  ...task,
  ...errors,
  ...keyword,
}
export default trans(lang, 'cn')
