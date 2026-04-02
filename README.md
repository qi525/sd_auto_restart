# WebUI 监控工具

## 快速安装
只需要下载`monitor_and_kill.py`文件即可，其他不需要下载。
最保守的话，可以使用reforge uv虚拟环境里面的python.exe
打开pwsh，粘贴以下命令

```powershell
C:\stable-diffusion-webui-reForge\venv\Scripts\python.exe "C:\个人数据\pythonCode\测试taskkill\monitor_and_kill.py"
```


cui好像只需要 python main.py --enable-manager
那你就写一个bat，单独存放这个python命令行即可。
C:\ComfyUI\venv\Scripts\python.exe "C:\个人数据\pythonCode\测试taskkill\monitor_and_kill.py"


"C:\个人数据\pythonCode\测试taskkill\monitor_and_kill.py" 这个路径改成你们自己的路径即可，随便你们放在哪里。


## 快速开始

### 方式一：直接运行（推荐）
双击 `monitor_and_kill.py` 文件即可启动监控程序。

### 方式二：命令行运行
```powershell
python monitor_and_kill.py
```

## 使用前配置

编辑 `monitor_and_kill.py` 文件，修改以下配置项：

```python
MONITOR_MODE = "webui"              # 选择模式: "webui" 或 "cui"
PID_CACHE = r"C:\...\webuipid.txt"  # PID缓存文件路径，会自动生成在py脚本对应位置，无需手动修改位置
WORK_DIR = r"C:\stable-diffusion-webui-reForge"  # 项目文件夹路径
BAT_FILE = "webui-user.bat"         # bat启动文件名
API_URL = "http://127.0.0.1:7861"   # webui API地址
FIXED_MONITOR_FOLDER = r"C:\...\output"  # CUI模式监控文件夹
CHECK_INTERVAL = 60                 # 检查间隔（秒）
MAX_NO_CHANGE_COUNT = 3             # 多少次无变化后重启
```

## 功能说明

- **自动监控**：监控输出文件夹，检测新文件生成
- **自动重启**：连续无新文件生成3次后自动重启WebUI
- **进程管理**：自动保存PID，进程异常退出时重启
- **模式切换**：支持WebUI和CUI两种监控模式

## 快速编辑模式禁用

为防止误操作导致程序冻结，已自动禁用Python的快速编辑模式。

## 常见问题

**Q: 双击py文件没有反应？**
- 确保已安装 Python 3.7+
- 确保 Python 已添加到系统 PATH
- 右键点击py文件，选择"用Python打开"

**Q: 怎样关闭监控？**
- 在命令窗口按 Ctrl+C 停止程序
- 或关闭命令窗口

**Q: 日志在哪里？**
- 所有日志输出到命令窗口，程序退出后消失
- 可自行修改代码添加日志文件记录功能
