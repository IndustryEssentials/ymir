# ymir-updater 使用指南

## 升级前的准备工作

1. 确认当前运行的 YMIR 系统版本是 1.1.0 版本，ymir-updater 不支持其他版本的升级
2. 确认 YMIR 中所有训练，挖掘及推理任务都已经停止，之后再停止 ymir 系统：bash ymir.sh stop
3. 建议备份 .env 的 YMIR_PATH 所指向的目录，默认为 YMIR 代码目录的 ymir-workplace
4. 确认升级所需硬盘空间是否足够：如果 ymir-workplace 占用 500G 硬盘空间，其中 ymir-assets 200G，则其余内容都会在升级过程中自动备份。即至少需要额外 300G 空间进行升级
5. 下载 YMIR 目标版本，并依据旧版本的配置修改 .env 文件
特别的，MYSQL_INITIAL_USER 及 MYSQL_INITIAL_PASSWORD 直接将旧版本的值复制过来。需要这些旧值登录
6. 如果位于内网，或是位于无法连接 dockerhub 的网络环境中，需要先取得与 YMIR 系统对应的升级镜像，镜像名称可以通过 docker-compose.updater.yml 中的 image 配置项得到
7. 如果使用 labelfree 作为标注工作，请注意 LabelFree 版本与 YMIR 版本的对应关系，YMIR 2.0.0 系统需要搭配 2.0.0 版本的 LabelFree 镜像运行

## 升级操作

确认上述准备工作做完以后，运行 bash ymir.sh update 进行升级，等待升级完成

## 常见问题

### 1. 升级脚本报错：sandbox not exists

原因：.env 中指定的 YMIR_PATH 或 BACKEND_SANDBOX_ROOT 错误，或者出现 ../ 符号

解决方案：检查 YMIR_PATH 和 BACKEND_SANDBOX_ROOT 的正确性，检查它们的值是否出现 ../ 符号

### 2. 升级完成后，mongodb 启动失败，并报错：could not find mysql_initial_user xxxx

原因：.env 文件中的 MYSQL_INITIAL_USER 和 MYSQL_INITIAL_PASSWORD 未按旧版本设置

解决方案：参考准备工作第 6 条

### 3. 升级完成后，或从备份回滚后启动系统时，mysql 启动失败，并报错：No permission

原因：准备工作第三步备份 ymir-workplace 时，可能更改了 ymir-workplace/mysql 目录本身及其文件的权限设置

解决方案：sudo chown -R 27:sudo ymir-workplace/mysql
