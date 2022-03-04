import trans from './trans'
import common from "./modules/common"
import dataset from "./modules/dataset"
import errors from "./modules/errors"
import login from "./modules/login"
import model from "./modules/model"
import routeTitle from "./modules/routeTitle"
import signup from "./modules/signup"
import task from "./modules/task"
import breadcrumbs from "./modules/breadcrumbs"
import portal from "./modules/portal"
import keyword from './modules/keyword'
import user from './modules/user'
import image from './modules/image'
import tip from './modules/tip'
import project from './modules/project'

export default {
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
  ...image,
  ...tip,
  ...project,
}
