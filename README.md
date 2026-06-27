# System Design and Compute Final Project — Trace Rover

> 系统设计与计算课程期末项目：基于 STM32H723 的麦克纳姆轮巡逻小车（Trace Rover）下位机控制工程。

本仓库为课程期末项目的源代码与文档归档，核心是一个运行在 **STM32H723VGTx（Cortex‑M7）** 上的嵌入式控制系统，负责小车的电机驱动、PWM 输出、串口通信以及与上位机的交互。整体工程使用 **Keil MDK‑ARM（uVision 5）+ ARMCLANG V6.19** 开发，同时支持 **Embedded IDE (EIDE)** 环境。

---

## 目录结构总览
```shell
system_design_and_compute_final_project/
├── LICENSE                    # 项目开源协议（MIT）
├── README.md                  # 项目说明文档（本文件）
├── .gitignore                 # Git 忽略规则
├── control/                   # 下位机嵌入式控制工程（STM32H723）
│   └── Trace_Rover/           # Keil MDK-ARM 工程根目录
│       ├── .eide/             # Embedded IDE 配置文件（可选）
│       ├── Core/              # 用户核心代码（Inc 头文件 + Src 源码）
│       ├── Drivers/           # HAL 驱动与 CMSIS 头文件
│       │   ├── CMSIS/         # ARM CMSIS 核心与 STM32H7 设备支持包
│       │   └── STM32H7xx_HAL_Driver/ # ST 官方 HAL 库源码
│       ├── MDK-ARM/           # Keil 工程文件、编译产物与调试配置
│       ├── .mxproject         # STM32CubeMX 项目记录
│       └── .clang-format      # C/C++ 代码格式化规则
├── software/                  # 上位机控制软件（PyQt5 + Python 3.11）
│   └── Trace_Rover_GC/        # Qt Creator 工程根目录
│       ├── .qtcreator/        # Qt Creator 工程配置与 Python 虚拟环境
│       ├── main.py            # 程序入口
│       ├── main_widget.py     # 主界面逻辑（配合 main_widget.ui）
│       ├── control_widget.py  # 手动控制面板逻辑
│       ├── pid_widget.py      # PID 参数调参面板逻辑
│       ├── main_func.py       # 主要功能调度
│       ├── trace_rover_comm.py # 与下位机的串口通信协议实现
│       ├── navigation.py      # 导航与路径规划模块
│       ├── mission.py         # 任务编排与执行模块
│       ├── vision.py          # 视觉图像处理模块（图传/识别）
│       ├── control.py         # 控制指令生成模块
│       ├── pid.py             # 上位机 PID 控制器实现
│       ├── config.py          # 全局配置参数
│       ├── utils.py           # 通用工具函数
│       ├── main_widget.ui     # 主界面 UI 设计文件
│       ├── control_widget.ui  # 控制面板 UI 设计文件
│       └── pid_widget.ui      # PID 调参面板 UI 设计文件
├── electronics/               # 硬件工程（嘉立创 EDA）
│   └── ProPrj_TraceRover_2026-03-28.epro2 # 嘉立创工程文件（原理图 + PCB）
├── structure/                 # 机械结构文件（SolidWorks）
│   ├── （模型装配体）.SLDASM   # 整车总装配体
│   ├── 上层装配1.SLDASM       # 上层板/传感器组件装配
│   ├── Board.step.STEP.SLDASM # 主板/PCB 安装支架装配
│   ├── Enter.step.STEP.SLDASM # 外壳/舱门部件装配
│   ├── Next.step.STEP.SLDASM  # 外壳/舱门部件装配
│   ├── J1/J3/J6.step.STEP.SLDASM # 连接器/接口部件装配
│   ├── ZDT_X28_L28Motor.STEP.SLDASM # 步进电机驱动板装配
│   ├── ZDT_X28_V1.2_PCB.step.STEP.SLDASM # 步进电机驱动板 PCB 装配
│   ├── 28_STEPPER_MOTOR.STEP.SLDPRT # 28 步进电机零件模型
│   ├── MC520编码器电机模型-升级款.step.SLDPRT # 带编码器的主驱动电机
│   ├── 80l/80r.SLDPRT         # 左右轮系零件
│   ├── 上层板绘制尝试.SLDPRT  # 上层板结构零件
│   ├── 底盘模型.SLDPRT        # 底盘结构零件
│   ├── 小车底盘壳.SLDPRT      # 底盘外壳零件
│   ├── 上下板连接铜柱.SLDPRT  # 连接件零件
│   ├── 支柱.SLDPRT            # 支撑零件
│   ├── PCB支柱.SLDPRT         # PCB 支撑零件
│   ├── 相机底座.SLDPRT        # 相机安装支架
│   ├── 相机柱.SLDPRT          # 相机支撑柱
│   ├── 相机柱80mm.SLDPRT      # 相机支撑柱（80mm）
│   ├── 电机延长轴.SLDPRT      # 传动零件
│   ├── 电机联轴器.SLDPRT      # 传动零件
│   ├── 滑环轴.SLDPRT          # 导电滑环轴
│   ├── 六角联轴器.step.SLDPRT # 联轴器零件
│   ├── 皮带1-1.SLDPRT         # 同步带零件
│   ├── 皮带线同步带-2.SLDPRT  # 同步带零件
│   ├── HTPA20S5M100_A_P6_35_a - 电机侧.SLDPRT # 同步带轮（电机侧）
│   ├── HTPA20S5M100_A_P6_35_a_导电滑环侧.SLDPRT # 同步带轮（滑环侧）
│   ├── ts-1145a-b-a_White.step.STEP.SLDPRT # 摄像头外壳
│   ├── 外壳终版.SLDPRT        # 最终版外壳外罩
│   ├── 电池.SLDPRT            # 电池盒模型
│   ├── 37电机支架.step.SLDPRT # 37 电机安装支架
│   ├── Sensor Ultrasónico.SLDPRT # 超声波传感器模型
│   ├── 图传发射模块.SLDPRT    # 图传发射模块外罩
│   ├── ZDT_X28_L28Motor.STEP  # 步进电机驱动板 STEP 模型
│   ├── ZDT_X28_V1.2.STEP.SLDPRT # 步进电机驱动板 PCB 模型
│   ├── WIRE_2.0.STEP.SLDPRT   # 线束模型
│   ├── SHIM_2.7x4x6.STEP.SLDPRT # 垫片模型
│   ├── Open CASCADE STEP translator 6.8 1.1.1.step.STEP.SLDPRT # 第三方 STEP 零件
│   ├── MT0522..FL.SLDPRT      # 法兰支架零件
│   ├── BREACKET.SLDPRT        # 通用支架零件
│   ├── PH2.0-WI-4P.step.STEP.SLDASM # PH2.0 连接器装配（4P）
│   ├── PH2.0-WI-8P.step.STEP.SLDASM # PH2.0 连接器装配（8P）
│   ├── PH2.0-WI-4P-0.step.STEP.SLDPRT # PH2.0 连接器单零件（4P）
│   ├── PH2.0-WI-8P-3.step.STEP.SLDPRT # PH2.0 连接器单零件（8P）
│   ├── PH2.0-WI--1.step.STEP.SLDPRT # PH2.0 连接器外壳
│   ├── PH2.0-WI-.step.STEP.SLDPRT # PH2.0 连接器锁片
│   ├── 6308926832.step.STEP.SLDASM # 采购件/标准件装配
│   └── 6308926992.step.STEP.SLDASM # 采购件/标准件装配
└── docs/                      # 项目文档与多媒体文件
    ├── 项目开题报告.pptx      # 开题答辩 PPT
    ├── 项目开题报告.pdf       # 开题报告 PDF
    ├── 项目结题报告.pptx      # 结题答辩 PPT
    ├── 项目结题报告.pdf       # 结题报告 PDF
    ├── 通信数据帧格式.xlsx    # 上下位机通信协议定义
    ├── 讲解视频.mp4           # 系统讲解视频
    ├── 宣传视频.mp4           # 项目宣传视频
    └── 合照.jpg               # 团队/实物合照
```

---

### 1. `docs/` — 项目文档与多媒体

`docs/` 目录是课程提交的核心资料，汇集了从开题到结题的全流程文档与展示素材，按用途可分为四组。

| 组别 | 文件 | 内容与用途 |
| --- | --- | --- |
| **开题阶段** | `项目开题报告.pptx`
`项目开题报告.pdf` | 项目立项资料：选题背景、系统需求分析、总体方案设计（机械结构 / 硬件电路 / 软件架构 / 通信协议）、预期功能与性能指标、时间节点规划。答辩用 PPT 及 PDF 定稿版本。 |
| **结题阶段** | `项目结题报告.pptx`
`项目结题报告.pdf` | 项目结项资料：系统实现细节、关键算法（电机 PID、路径规划、上位机交互）、测试与实验结果、性能分析、问题与改进总结。答辩用 PPT 及 PDF 定稿版本。 |
| **通信协议** | `通信数据帧格式.xlsx` | **上位机‑下位机通信的数据帧规范文档**。定义了帧头、设备地址、功能码、数据域、校验和（异或校验）、帧尾等字段的字节排列、大小端、单位与取值范围；同时列出了小车运行、停止、速度调节、转向、状态回传等命令码。是两端软件联调的契约文件。 |
| **展示素材** | `讲解视频.mp4` | 功能讲解视频：对系统整体方案、硬件组成、软件流程、现场演示进行讲解，用于课程答辩与成果展示。 |
| | `宣传视频.mp4` | 项目宣传视频：展示小车外观、运行效果与亮点功能，用于课程作业展示、宣传或评奖材料。 |
| | `合照.jpg` | 项目团队合照 / 小车实物合照，作为结题资料存档。 |

> **重点提示**：
> - `通信数据帧格式.xlsx` 是软件开发人员的首要参考文档，定义了上位机与下位机之间的字节级通信契约。
> - `项目结题报告.pdf` / `.pptx` 是对整个项目架构、实现与测试最完整的文字化总结，建议作为阅读代码前的前置资料。
> - 两份视频分别面向"功能讲解"与"成果宣传"两种场景，按需观看。

---

## 各文件夹及文件功能详解

### 2. `control/Trace_Rover/` — 下位机控制工程（STM32H723）

这是项目的核心工程目录，对应一辆名为 **Trace Rover** 的履带式巡逻小车的下位机固件。

| 子目录/文件 | 功能说明 |
| --- | --- |
| `.eide/` | Embedded IDE（VS Code 插件）的工程配置：
- `eide.yml`：EIDE 工程主配置
- `env.ini`：构建环境变量
- `files.options.yml`：文件级编译选项
- `trace_rover.st.option.bytes.ini`：STM32 选项字节配置 |
| `.cmsis/` | CMSIS 设备模板，包含 ARM Cortex‑A/M 系列的启动代码、链接脚本与内核头文件，用于多芯片支持 |
| `Core/Inc/` | 用户头文件：`main.h`、`gpio.h`、`tim.h`、`usart.h`、`stm32h7xx_it.h`、`stm32h7xx_hal_conf.h` |
| `Core/Src/` | 用户源代码，详见下方小节 |
| `Drivers/CMSIS/` | ARM CMSIS 核心头文件（`core_cm7.h` 等）、编译器适配层，以及 STM32H7 设备寄存器定义（`stm32h723xx.h`） |
| `Drivers/STM32H7xx_HAL_Driver/` | ST 官方 HAL 库：`Inc/` 提供外设驱动头文件，`Src/` 为对应实现（GPIO、UART、TIM、DMA、RCC、PWR、FLASH、I2C、EXTI 等） |
| `MDK-ARM/` | Keil uVision5 工程：
- `Trace_Rover.uvprojx` / `.uvoptx`：工程与选项文件
- `DebugConfig/*.dbgconf`：调试配置
- `RTE/_Trace_Rover/RTE_Components.h`：运行时组件头文件
- `Trace_Rover/`：编译产物（`.axf`、`.hex`、`.map`、`.htm` 等） |
| `.mxproject` | STM32CubeMX 生成/记录文件，表明工程由 CubeMX 初始化后进行二次开发 |
| `.clang-format` | 统一的代码风格配置文件，便于 CLion / VS Code / Keil 等 IDE 自动格式化 |

> **值得注意的编译产物线索**：从 `MDK-ARM/Trace_Rover/` 下的 `.o` 目标文件可以反向推断出工程中实际存在但未在 `Core/Src/` 目录显式出现的业务模块——`actuator.o`、`comm.o`、`fsm.o`、`filter.o`、`tasks.o`、`time_slice.o`、`ultrasonic.o`、`pid.o`、`coordinate2d.o`、`mecanum.o`、`fifo.o`。这些模块分别实现了执行器控制、通信协议、有限状态机（FSM）、滤波、任务调度、时间片轮转、超声波采集、PID、坐标变换、麦轮运动学解算等核心功能，是整个下位机控制的"真正大脑"。

#### `Core/Src/` 源码解读

| 文件 | 功能 |
| --- | --- |
| `main.c` | **程序入口**。初始化 HAL、配置系统时钟（HSE + PLL，主频 550 MHz 级别）、初始化 GPIO / TIM1/2/3/4/5/8/15 / USART1/2/3，然后调用 `tasks_init()` 并在主循环中执行 `tasks_run()` 进行调度。 |
| `gpio.c` | GPIO 初始化：LED、按键、电机方向控制引脚等 |
| `tim.c` | 定时器初始化：TIM1/TIM8 用于 PWM 驱动电机，TIM2/TIM3/TIM4/TIM5 用于输入捕获或编码器测速，TIM15 用于周期性中断（任务调度/心跳） |
| `usart.c` | 串口初始化：USART1/2/3，分别对应上位机通信、调试串口、外部传感器/模块通信 |
| `stm32h7xx_it.c` | 中断服务例程（HardFault、SysTick、UART、TIM 等） |
| `stm32h7xx_hal_msp.c` | HAL 底层初始化（GPIO 复用、时钟使能、DMA 配置） |
| `system_stm32h7xx.c` | 系统启动文件与向量表相关辅助函数 |

---

### 3. `software/Trace_Rover_GC/` — 上位机控制软件（PySide6 + Python 3.11）

这是运行在 PC 端的上位机图形化控制程序，使用 **Qt Creator** 作为 UI 设计工具，运行在 **Python 3.11** 虚拟环境中。主要功能包括：手动遥控小车、下发运动指令、实时回传并显示小车状态数据、PID 参数在线调参、视觉图像（图传画面）显示与处理、以及按任务序列自动巡航。

#### 核心 Python 源文件

| 文件 | 功能 |
| --- | --- |
| `main.py` | **程序入口**。初始化 QApplication、加载主窗口 `main_widget`、启动事件循环。 |
| `main_widget.py` | 主界面逻辑实现。整合串口状态显示、连接按钮、手动/自动模式切换、小车状态面板、图像显示区、日志窗口等。配合 `main_widget.ui` 共同描述界面布局。 |
| `control_widget.py` | **手动控制面板逻辑**。提供开环、速度闭环与位置闭环再不同坐标系下控制等操作入口，通过 `control.py` 与 `trace_rover_comm.py` 下发指令。 |
| `pid_widget.py` | **PID 参数调参面板**。提供 P/I/D 三系数的输入框、读写按钮、载入与保存参数按钮，通过串口与下位机同步参数。 |
| `main_func.py` | **主功能调度器**。整合 `navigation`、`mission`、`vision`、`control`、`pid` 等模块，在主循环中按帧处理：解析传感器数据 → 更新状态 → 生成控制量 → 下发下位机。 |
| `trace_rover_comm.py` | **串口通信协议核心**。按照 `docs/通信数据帧格式.xlsx` 中定义的字节顺序、校验规则，实现：- 帧打包（添加帧头、功能码、CRC/异或校验、帧尾）- 帧解包（校验、拆分字段、以事件回调方式通知上层）- 指令码枚举（运行、导航、PID 读写、心跳、版本查询等） |
| `navigation.py` | **导航可视化模块**。读取下位机返回的导航数据，实时绘制小车位置、速度、障碍物等信息。 |
| `mission.py` | **任务编排与执行模块**。以航点表或时间线形式组织一次任务："到达 A 点 → 旋转摄像头 → 等待 2 秒 → 返回起点"。由 `main_func.py` 按状态机推进。 |
| `vision.py` | **视觉图像处理模块**。读取 USB 摄像头或图传接收机画面，进行简单处理（去畸变、裁剪、在画面上叠加坐标/速度文字），并把图像渲染到 `main_widget` 的显示区，并可以接入YOLO26模型进行目标检测、ArUco标记识别修正导航坐标。 |
| `control.py` | **控制指令生成模块**。把上位机用户输入或导航模块给出的目标速度/角速度/坐标，换算为符合通信协议格式的指令帧，并调用 `trace_rover_comm.py` 下发。 |
| `pid.py` | **上位机 PID 调参实现**。读取 `pid_widget.py` 中的 P/I/D 参数，通过串口与下位机同步参数。 |
| `config.py` | **全局配置**。串口号、波特率、小车物理参数（轮径、轮距、最大速度、加速度限制）、导航坐标原点、摄像头分辨率与设备号等。 |
| `utils.py` | **通用工具函数**。数据类型转换（int↔bytes、大小端）、坐标变换、CRC 计算、日志工具、时间戳生成。 |

#### UI 设计文件（Qt Designer / Qt Creator）

| 文件 | 说明 |
| --- | --- |
| `main_widget.ui` | 主窗口布局：顶部菜单栏、左侧控制按钮区、中央图像显示区、右侧状态面板、底部日志区。 |
| `control_widget.ui` | 手动控制面板的独立布局文件；以子窗口或 tab 页形式嵌入主界面。 |
| `pid_widget.ui` | PID 调参面板布局：P/I/D 参数输入框、目标/当前值显示、曲线画布（使用 QCustomPlot 或 Matplotlib）。 |

#### 虚拟环境与配置

| 目录/文件 | 说明 |
| --- | --- |
| `.qtcreator/Python_3_11_7venv/` | Qt Creator 自动创建的 Python 3.11 虚拟环境，内含 `pip`、`setuptools`、`pkg_resources`、`distutils` 等基础包；项目运行时需先在此环境中安装 `PySide6`、`pyserial`、`numpy`、`opencv-python`、`matplotlib` 等依赖。 |

> **运行方式**：在 Qt Creator 中打开工程根目录（或直接在命令行 `python main.py`），选择正确的串口并点击连接，即可通过界面控制小车运动、观察图传画面、调参或触发自动任务。

---

### 4. `electronics/` — 硬件工程（嘉立创 EDA）

`electronics/` 目录中包含小车的完整硬件设计工程，使用国产 EDA 工具 **嘉立创 EDA（LCEDA / EasyEDA Pro）** 设计，文件格式为 `.epro2`。

| 文件 | 功能说明 |
| --- | --- |
| `ProPrj_TraceRover_2026-03-28.epro2` | **嘉立创工程文件**（一个文件即包含原理图 + PCB 叠层设计）。工程名为 "TraceRover"，创建/最后修改日期为 2026‑03‑28。通常内部包括：① **主控板**（STM32H723VGTx 最小系统 + USB 转串口 + 电源输入）；② **电机驱动通道**（PWM/方向/使能信号引出到大电流 H桥）；③ **传感器接口**（编码器正交信号、超声波 IO、IMU I2C/SPI）；④ **通信接口**（USART1 连上位机、USART2 调试、USART3 外接）；⑤ **电源管理**（从电池降压到 5V / 3V3，兼顾电机与传感器）；⑥ **预留拓展**（图传模块、舵机云台、摄像头接口）。 |

> **使用方式**：在嘉立创 EDA 客户端中直接双击 `.epro2` 打开；也可通过"嘉立创下单助手"直接导出 Gerber / BOM / 坐标文件进行 PCB 打样。如需查看 PDF 版原理图或装配图，可在嘉立创 EDA 中导出。

---

### 5. `structure/` — 机械结构（SolidWorks）

`structure/` 目录中集中存放 **SolidWorks** 的零件与装配体文件，对应一辆完整的履带式小车。按照"**结构件 → 传动件 → 连接件 → 外购件/标准件 → 总装配**"的思路，可以将文件分为以下类别：

#### ① 总装配与子装配（`.SLDASM`）

| 文件 | 说明 |
| --- | --- |
| `（模型装配体）.SLDASM` | **整车总装配**，集成底盘、上层板、电机、履带、相机、电池、PCB 支架等所有零件。 |
| `上层装配1.SLDASM` | 上层板及传感器组件的装配（相机支架、铜柱、图传模块等）。 |
| `Board.step.STEP.SLDASM` | PCB / 主控板安装支架的装配。 |
| `Enter.step.STEP.SLDASM` / `Next.step.STEP.SLDASM` | 外壳相关的子装配体，用于覆盖车身并预留接口。 |
| `J1/J3/J6.step.STEP.SLDASM` | 不同规格连接器在整机中的装配单元。 |
| `ZDT_X28_L28Motor.STEP.SLDASM` | 28 步进电机驱动板的装配体。 |
| `ZDT_X28_V1.2_PCB.step.STEP.SLDASM` | 步进电机驱动板 PCB 的装配体版本。 |
| `6308926832.step.STEP.SLDASM` / `6308926992.step.STEP.SLDASM` | 外购件/标准件（编号来自供应商或在线 3D 零件库）的 STEP 装配体。 |
| `PH2.0-WI-4P.step.STEP.SLDASM` / `PH2.0-WI-8P.step.STEP.SLDASM` | PH2.0 连接器（4 针/8 针）的完整装配。 |

#### ② 结构件与外壳（`.SLDPRT`）

| 文件 | 说明 |
| --- | --- |
| `上层板绘制尝试.SLDPRT` | 上层板原始建模，用于搭载主控板和传感器。 |
| `底盘模型.SLDPRT` / `小车底盘壳.SLDPRT` | 底盘基础结构，用于承载电机、电池、驱动器。 |
| `外壳终版.SLDPRT` | 最终定型的外壳外罩，保护内部结构。 |
| `电池.SLDPRT` | 电池盒模型。 |
| `支柱.SLDPRT` / `上下板连接铜柱.SLDPRT`（含若干副本）| 上下层连接支柱系列（不同长度/接口）。 |
| `PCB支柱.SLDPRT` | PCB 专用安装支柱。 |
| `BREACKET.SLDPRT` | 通用小型支架。 |
| `MT0522..FL.SLDPRT` | 另一种法兰类支架零件。 |

#### ③ 相机 / 图传 / 传感器件（`.SLDPRT`）

| 文件 | 说明 |
| --- | --- |
| `相机底座.SLDPRT` / `相机柱.SLDPRT` / `相机柱80mm.SLDPRT` | 相机安装支架系列（不同高度/角度）。 |
| `图传发射模块.SLDPRT` | 图传发射模块外壳/安装件。 |
| `ts-1145a-b-a_White.step.STEP.SLDPRT` | 配套的摄像头外壳（白色，常见 3D 打印件）。 |
| `Sensor Ultrasónico.SLDPRT` | 超声波传感器（HC‑SR04 等）模型。 |

#### ④ 电机 / 传动件（`.SLDPRT`）

| 文件 | 说明 |
| --- | --- |
| `28_STEPPER_MOTOR.STEP.SLDPRT` | 28 步进电机零件。 |
| `MC520编码器电机模型-升级款.step.SLDPRT` | **主驱动电机**（带编码器），用于左右履带。 |
| `37电机支架.step.STEP.SLDPRT` | 37 直流减速电机安装支架。 |
| `电机延长轴.SLDPRT` / `电机联轴器.SLDPRT` | 电机延长轴与联轴器。 |
| `滑环轴.SLDPRT` | **导电滑环** 安装轴，解决旋转部件的供电/信号走线。 |
| `六角联轴器.step.SLDPRT` | 六角联轴器零件。 |
| `皮带1-1.SLDPRT` / `皮带线同步带-2.SLDPRT` | 同步带零件（不同长度/齿距）。 |
| `HTPA20S5M100_A_P6_35_a - 电机侧.SLDPRT` | 电机侧同步带轮。 |
| `HTPA20S5M100_A_P6_35_a_导电滑环侧.SLDPRT` | 滑环侧同步带轮。 |
| `ZDT_X28_L28Motor.STEP` / `ZDT_X28_V1.2.STEP.SLDPRT` | 步进电机驱动板的原始 STEP 零件与 SolidWorks 零件。 |

#### ⑤ 轮系与行走部分（`.SLDPRT`）

| 文件 | 说明 |
| --- | --- |
| `80l.SLDPRT` / `80r.SLDPRT` / `80l.2.SLDPRT` / `80r.2.SLDPRT` | **左右轮系**零件的 1 版与 2 版迭代。 |
| `SHIM_2.7x4x6.STEP.SLDPRT` | 调整间隙用垫片。 |

#### ⑥ 连接器与线束（`.SLDPRT`）

| 文件 | 说明 |
| --- | --- |
| `PH2.0-WI-4P-0.step.STEP.SLDPRT` / `PH2.0-WI-8P-3.step.STEP.SLDPRT` | PH2.0 连接器（4P/8P）的单零件模型。 |
| `PH2.0-WI-____-1.step.STEP.SLDPRT` / `PH2.0-WI-____.step.STEP.SLDPRT` | PH2.0 连接器外壳/锁片（占位型号）。 |
| `WIRE_2.0.STEP.SLDPRT` | 2.0 mm 线束模型。 |

#### ⑦ 导入的第三方 STEP 零件

| 文件 | 说明 |
| --- | --- |
| `Open CASCADE STEP translator 6.8 1.1.1.step.STEP.SLDPRT` | 经 Open CASCADE 工具从外部 STEP 转换后导入的零件。 |

> **使用建议**：先用 SolidWorks 打开 `（模型装配体）.SLDASM` 查看整车装配关系；之后可按装配树逐层查看各零件；如要修改，建议以 `.SLDPRT` 为单位在零件模式下编辑，改动较大时注意配合 `electronics/` 中的 PCB 工程重新验证安装孔与连接器位置。

---

## 软件架构概览
```shell
┌─────────────────────────────────────────────┐
│ 上位机 (PC / software/Trace_Rover_GC)        │
│ ┌──────────────────────────────────────┐    │
│ │ main_widget + control_widget         │    │ ← 图形化 UI
│ │ (PySide6: 手动控制 / PID 调参 / 图传)  │    │
│ └──────────────┬────────────────────────┘    │
│                │                             │
│ ┌──────────────▼────────────────────────┐    │
│ │ control.py / pid.py / navigation.py   │    │
│ │ mission.py / vision.py                │    │
│ └──────────────┬────────────────────────┘    │
│                │                             │
│ ┌──────────────▼────────────────────────┐    │
│ │ trace_rover_comm.py (协议打包/解包)    │    │
│ └──────────────┬────────────────────────┘    │
└────────────────┼─────────────────────────────┘
                 │
                 │ 串口 (UART, 波特率详见 config.py)
                 │ 协议格式：docs/通信数据帧格式.xlsx
                 ▼
┌─────────────────────────────────────────────┐
│ STM32H723VGTx (Cortex-M7, 550MHz)           │
│ ┌────────────────────────────────────────┐  │
│ │ tasks_run() 调度循环                    │  │
│ │ ├─ comm_task()  ─► 帧解析/打包          │  │
│ │ ├─ actuator_task() ─► 电机 PWM / 舵机   │  │
│ │ ├─ sense_task() ─► 编码器/超声波采集     │  │
│ │ ├─ fsm_task() ─► 有限状态机             │  │
│ │ ├─ pid_task() ─► 速度环/位置环 PID      │  │
│ │ └─ report_task() ─► 状态回传上位机      │  │
│ └────────────────────────────────────────┘  │
│ HAL Driver (TIM / UART / GPIO / DMA)        │
└─────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│ 左右电机 │ 编码器 │ 传感器/图传               │
└─────────────────────────────────────────────┘
```
---

## 构建与烧录

### 下位机（`control/Trace_Rover/`）

1. **使用 Keil MDK‑ARM**：
   - 打开 `control/Trace_Rover/MDK-ARM/Trace_Rover.uvprojx`
   - 确认已安装 `Keil.STM32H7xx_DFP.4.0.0` 支持包
   - 选择目标 `Trace_Rover`，执行 **Build** 生成 `Trace_Rover.hex`
   - 使用 ST‑Link / J‑Link 烧录到 STM32H723VGTx

2. **使用 Embedded IDE (EIDE)**：
   - 在 VS Code 中安装 EIDE 插件
   - 导入 `control/Trace_Rover/.eide/eide.yml`
   - 选择工具链并编译/下载

### 上位机（`software/Trace_Rover_GC/`）

1. 创建并激活 Python 3.11 虚拟环境（或复用 `.qtcreator/Python_3_11_7venv`）
2. 安装依赖：`pip install PyQt5 pyserial numpy opencv-python matplotlib`
3. 在项目根目录执行 `python main.py`，或在 Qt Creator 中直接运行

### 通信协议参考

详见 `docs/通信数据帧格式.xlsx`，其中定义了上下位机之间所有的帧格式与指令码。

---

## 许可协议

本项目采用 **MIT License**，详见根目录 `LICENSE` 文件。