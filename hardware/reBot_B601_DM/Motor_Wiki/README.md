# 电机厂商 Wiki 文档

> 使用 OpenCLI 从 wiki.seeedstudio.com 抓取的官方教程，离线保存方便查阅。
> 抓取日期：2026.04.14

## 文档列表

| 文件夹 | 来源 | 说明 |
|--------|------|------|
| **达妙系列电机** | [wiki.seeedstudio.com/cn/damiao_series/](https://wiki.seeedstudio.com/cn/damiao_series/) | 达妙 43 系列电机完整教程（规格参数、CAN 协议、C++/Python 控制） |
| **RobStride_电机控制完整指南** | [wiki.seeedstudio.com/cn/robstride_control/](https://wiki.seeedstudio.com/cn/robstride_control/) | RobStride 电机多语言控制（Python/C++/Rust/Arduino） |
| **DM_Gripper_-_Assembly_Guide_with_Demo** | [wiki.seeedstudio.com/dm_gripper/](https://wiki.seeedstudio.com/dm_gripper/) | 达妙夹爪组装指南和演示 |

## 与本项目的关系

- **reBot-DevArm B601-DM 版**使用达妙 DM4340P（大关节）和 DM4310（小关节）
- **reBot-DevArm B601-RS 版**将使用 RobStride 电机
- **DM Gripper** 是可选的末端执行器（夹爪）

## 相关资源

- 电机 PDF 规格书：`../Motor_Datasheets/`
- 底层驱动代码：`../../../software/MotorBridge/`
- 软件侧也有一份副本：`../../../software/wiki_docs/`
