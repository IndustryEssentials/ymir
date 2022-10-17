# ymir 1.2.2 - 1.3.0 升级指南

1. 确认当前运行的 ymir 系统版本是 1.2.2 版本
2. 确认 ymir 中所有训练，挖掘及推理任务都已经停止，之后再停止 ymir 系统：`./ymir.sh stop`
3. 备份 ymir-workplace 目录（如果空间不够，可以略过 ymir-assets 目录）
4. 下载 ymir 1.3.0 版本，并依据旧版本的配置修改 .env 文件
5. 如果是内网，需要先取得升级镜像：`industryessentials/ymir-updater:1.2.2-1.3.0`
6. 运行 `./ymir.sh update` 进行升级，等待升级完成
7. 升级完成后，启动 ymir 1.3.0 版本
