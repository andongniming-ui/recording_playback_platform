# Recording Playback Platform Workspace

这个目录是整理后的工作区，平台本体和被测系统已经分开：

- `platform/`
  录制回放平台本体，包含 `backend`、`frontend`、`docs`、`data`、`ssh_keys`
- `systems-under-test/`
  被测系统样例，当前包含 `didi/`、`waimai/`、`loan-system/`
- `runtime/`
  运行时目录，日志统一写到 `runtime/logs/`
- `start-all.sh` / `stop-all.sh`
  根目录统一启动和停止入口

常用命令：

```bash
cd /home/recording_playback_platform
./start-all.sh platform
./start-all.sh didi
./start-all.sh all
```

入口文档：

- 平台说明：`platform/README.md`
- didi：`systems-under-test/didi/README.md`
- waimai：`systems-under-test/waimai/README.md`
- loan-system：`systems-under-test/loan-system/README.md`
