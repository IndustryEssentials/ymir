export const homeRoutes = [
  {
    path: "/home",
    name: "home",
    redirect: "/home/portal",
    title: 'portal.title',
    breadcrumbName: 'portal.title',
  },
  {
    path: "/home/portal",
    name: "portal",
    component: "@/pages/portal/index",
    title: 'portal.title',
    breadcrumbName: 'portal.title',
  },
  {
    path: "/home/task/fusion/:id",
    name: "taskFilter",
    component: "@/pages/task/fusion/index",
    title: 'task.fusion.title',
  },
  {
    path: "/home/task/mining/:id?",
    name: "taskMining",
    component: "@/pages/task/mining/index",
    title: 'task.mining.title',
  },
  {
    path: "/home/task/train/:id?",
    name: "taskTrain",
    component: "@/pages/task/train/index",
    title: 'task.train.title',
  },
  {
    path: "/home/task/label/:id",
    name: "taskTrain",
    component: "@/pages/task/label/index",
    title: 'task.label.title',
  },
  {
    path: "/home/task/copy/:id",
    name: "taskCopy",
    component: "@/pages/task/copy/index",
    title: 'dataset.copy.title',
  },
  {
    path: "/home/dataset/add/:pid",
    name: "datasetImport",
    component: "@/pages/dataset/add",
    title: "dataset.add.title",
  },
  {
    path: "/home/dataset/detail/:id",
    name: "datasetDetail",
    component: "@/pages/dataset/detail",
    title: "dataset.title",
  },
  {
    path: "/home/dataset/assets/:id",
    name: "datasetDetail",
    component: "@/pages/dataset/assets",
    title: "dataset.assets.title",
  },
  {
    path: "/home/model/detail/:id",
    name: "modelDetail",
    component: "@/pages/model/detail",
    title: "model.title",
  },
  {
    path: "/home/history/:type/:id",
    name: "history",
    component: "@/pages/history/index",
    title: "history.title",
  },
  {
    path: "/home/model/verify/:id",
    name: "modelVerify",
    component: "@/pages/model/verify",
    title: "model.verify.title",
  },
  {
    path: "/home/modify_pwd",
    component: "@/pages/user/modifyPwd",
    title: "modify_pwd.title",
  },
  {
    path: "/home/keyword",
    name: "keyword",
    component: "@/pages/keyword/index",
    title: "keywords.title",
  },
  {
    path: "/home/user",
    name: "user",
    component: "@/pages/user/info",
    title: "keywords.title",
  },
  {
    path: "/home/image",
    name: "image",
    component: "@/pages/image/index",
    title: "images.title",
  },
  {
    path: "/home/image_center",
    name: "imageCenter",
    component: "@/pages/image/center",
    title: "images.center.title",
  },
  {
    path: "/home/image/detail/:id",
    name: "imageDetail",
    component: "@/pages/image/detail",
    title: "image.title",
  },
  {
    path: "/home/image/add/:id?",
    name: "imageAdd",
    component: "@/pages/image/add",
    title: "image.add.title",
  },
  {
    path: "/home/permission",
    name: "permission",
    component: "@/pages/user/permission",
    title: "user.permission.title",
  },
  {
    path: "/home/project",
    name: "project",
    component: "@/pages/project/index",
    title: "projects.title",
  },
  {
    path: "/home/project/detail/:id",
    name: "projectDetail",
    component: "@/pages/project/detail",
    title: "project.title",
  },
  {
    path: "/home/project/add/:id?",
    name: "projectAdd",
    component: "@/pages/project/add",
    title: "project.add.title",
  },
  {
    path: "/home/project/interation/:pid",
    name: "projectInteration",
    component: "@/pages/project/interation",
    title: "project.interation.title",
  },
]
const Routes = [
  {
    path: "/home",
    component: "@/layouts/index",
    routes: homeRoutes.map(({ path, name, component, title = '' }) => ({ path, name, component, title })),
  },
  {
    path: "/",
    component: "@/layouts/unauth",
    routes: [
      {
        path: "/",
        redirect: "/home/project",
      },
      {
        path: "/login",
        component: "@/pages/user/login",
        title: "login.title",
      },
      {
        path: "/forget_pwd",
        component: "@/pages/user/forget",
        title: "forget.title",
      },
      {
        path: "/reset_pwd/:token",
        component: "@/pages/user/resetPwd",
        title: "reset_pwd.title",
      },
      {
        path: "/signup",
        component: "@/pages/user/signup",
        title: "signup.title",
      },
    ],
  },
]

export default Routes
