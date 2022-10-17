# ymir 1.2.2 - 1.3.0 升级指南

1. 确认当前运行的 ymir 系统版本是 1.2.2 版本
2. 确认 ymir 中所有训练，挖掘及推理任务都已经停止，之后再停止 ymir 系统：`bash ./ymir.sh stop`
3. 备份 ymir-workplace 目录
    * 如果空间不够，可以略过 ymir-assets 目录及 work_dir/CMD_INFERENCE 目录
    * 备份的 cp 命令加上 --preserve=links 参数，例如 `sudo cp -r --preserve=links ./ymir-workplace /xxx/ymir-workplace-122`
4. 确认升级所需硬盘空间是否足够：如果 ymir-workplace 占用 500G 硬盘空间，其中 ymir-assets 200G，则至少需要额外 300G 空间进行升级
5. 下载 ymir 1.3.0 版本，并依据旧版本的配置修改 .env 文件
    * 特别的，`MYSQL_INITIAL_USER` 及 `MYSQL_INITIAL_PASSWORD` 直接将旧版本的值复制过来
6. 如果是内网，需要先取得升级镜像：`industryessentials/ymir-updater:1.2.2-1.3.0`
7. 新版系统需要搭配 0.2.2 版本的 LabelFree 镜像运行
8. 确认上述准备工作做完以后，运行 `bash ./ymir.sh update` 进行升级，等待升级完成
9. 升级完成后，启动 ymir 1.3.0 版本