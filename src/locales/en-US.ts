import trans from './trans'
import task from "./modules/task"
import dataset from "./modules/dataset"
import errors from "./modules/errors"
import forget from "./modules/forget"
import login from "./modules/login"
import model from "./modules/model"
import modify_pwd from "./modules/modify_pwd"
import reset_pwd from "./modules/reset_pwd"
import routeTitle from "./modules/routeTitle"
import signup from "./modules/signup"
import common from "./modules/common"
import breadcrumbs from "./modules/breadcrumbs"
import portal from "./modules/portal"

const lang = {
  ...common,
  ...routeTitle,
  ...breadcrumbs,
  ...portal,
  ...login,
  ...signup,
  ...modify_pwd,
  ...reset_pwd,
  ...forget,
  ...dataset,
  ...model,
  ...task,
  ...errors,
}
export default trans(lang, 'en')
