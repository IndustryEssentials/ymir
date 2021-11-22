const Routes = [
  {
    path: "/home",
    component: "@/layouts/index",
    routes: [
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
        path: "/home/task",
        name: "task",
        component: "@/pages/task/index",
        title: 'tasks.title',
      },
      {
        path: "/home/task/s/:keyword?",
        name: "taskS",
        component: "@/pages/task/index",
        title: 'tasks.title',
      },
      {
        path: "/home/task/detail/:id",
        name: "taskDetail",
        component: "@/pages/task/detail",
        title: 'task.title',
      },
      {
        path: "/home/task/filter/:ids?",
        name: "taskFilter",
        component: "@/pages/task/filter/index",
        title: 'task.filter.title',
      },
      {
        path: "/home/task/mining/:ids?",
        name: "taskMining",
        component: "@/pages/task/mining/index",
        title: 'task.mining.title',
      },
      {
        path: "/home/task/train/:ids?",
        name: "taskTrain",
        component: "@/pages/task/train/index",
        title: 'task.train.title',
      },
      {
        path: "/home/task/label/:id?",
        name: "taskTrain",
        component: "@/pages/task/label/index",
        title: 'task.label.title',
      },
      {
        path: "/home/dataset",
        name: "dataset",
        component: "@/pages/dataset/index",
        title: "datasets.title",
      },
      {
        path: "/home/dataset/s/:keyword?",
        name: "datasetS",
        component: "@/pages/dataset/index",
        title: "datasets.title",
      },
      {
        path: "/home/dataset/detail/:id",
        name: "datasetDetail",
        component: "@/pages/dataset/detail",
        title: "dataset.title",
      },
      {
        path: "/home/dataset/asset/:id/:hash",
        name: "datasetAsset",
        component: "@/pages/dataset/asset",
        title: "asset.title",
      },
      {
        path: "/home/model",
        name: "model",
        component: "@/pages/model/index",
        title: "models.title",
      },
      {
        path: "/home/model/s/:keyword?",
        name: "modelS",
        component: "@/pages/model/index",
        title: "models.title",
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
    ],
  },
  {
    path: "/",
    component: "@/layouts/unauth",
    routes: [
      {
        path: "/",
        redirect: "/home/portal",
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
