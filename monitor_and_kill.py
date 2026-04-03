import subprocess
import os
import time
import json
from datetime import datetime
import psutil

# ===========================================手动更改位置===========================================

# ========== 监控模式选择 ==========
MONITOR_MODE = "webui"  # 选择监控模式: "webui" 或 "cui"
# webui模式: 每天自动生成监控文件夹路径 (例如: C:\stable-diffusion-webui-reForge\outputs\txt2img-images\2026-03-01)
# cui模式: 固定监控一个文件夹 (例如: C:\ComfyUI\output)

WORK_DIR = r"C:\stable-diffusion-webui-reForge" # 项目文件夹路径，须手动更改
BAT_FILE = "webui-user.bat" # bat启动项目录路径（相对于WORK_DIR），如果是webui应该不用改，cui不清楚。用户只要保证是bat类型文件，且这个bat文件存在就行了。
API_URL = "http://127.0.0.1:7861"  # webui的API地址（默认端口7860）【我魔改了端口为7861，因为测试的东西比较多，用户们需要自己自行修改web端口】

# ========== CUI模式专用 ==========
FIXED_MONITOR_FOLDER = r"C:\ComfyUI\output"  # CUI模式时的固定监控文件夹路径，需要自行修改

# ========== 监控设置 ==========
CHECK_INTERVAL = 60  # 1分钟检查一次
MAX_NO_CHANGE_COUNT = 3  # 连续无变化3次则重启

# PID缓存文件路径（自动获取当前脚本所在目录）,用户无需修改
PID_CACHE = os.path.join(os.path.dirname(__file__), "webuipid.txt") 
# ===========================================手动更改位置===========================================

def get_timestamp():
    """获取当前时间戳 格式: HH:MM:SS"""
    return datetime.now().strftime("%H:%M:%S")


def save_pid(pid):
    """保存PID到缓存文件"""
    with open(PID_CACHE, 'w') as f:
        f.write(str(pid))
    print(f"[{get_timestamp()}] [✓] PID {pid} 已保存到 {PID_CACHE}")

def load_pid():
    """从缓存文件读取PID"""
    if os.path.exists(PID_CACHE):
        try:
            with open(PID_CACHE, 'r') as f:
                pid = int(f.read().strip())
            return pid
        except:
            return None
    return None

def pid_exists(pid):
    """检查PID是否存在"""
    try:
        psutil.Process(pid)
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False
    
# Agent Scheduler webui的插件 API
# def get_queue_status():
#     """获取scheduler队列状态"""
#     try:
#         response = requests.get(
#             f"{API_URL}/agent-scheduler/v1/queue",
#             params={"limit": 100, "offset": 0},
#             timeout=5
#         )
#         
#         if response.status_code == 200:
#             data = response.json()
#             total_tasks = data.get("total_pending_tasks", 0)
#             return True, total_tasks
#     except Exception as e:
#         print(f"[{get_timestamp()}] [!] 获取队列失败: {e}")
#     return False, None

def get_monitor_folder():
    """获取监控文件夹 - 根据模式返回不同路径"""
    if MONITOR_MODE == "webui":
        # WebUI模式: 每天自动生成路径
        today = datetime.now().strftime("%Y-%m-%d")
        folder = os.path.join(WORK_DIR, "outputs", "txt2img-images", today)
    elif MONITOR_MODE == "cui":
        # CUI模式: 使用固定路径
        folder = FIXED_MONITOR_FOLDER
    else:
        raise ValueError(f"未知的监控模式: {MONITOR_MODE}，请设置为 'webui' 或 'cui'")
    return folder

def get_today_folder():
    """[弃用] 保留此函数以兼容旧代码，建议使用 get_monitor_folder()"""
    return get_monitor_folder()

def get_file_count(folder):
    """获取文件夹中的文件数量"""
    if not os.path.exists(folder):
        return 0
    return len([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))])

def start_webui():
    """启动webui"""
    cmd = [
        "pwsh",
        "-NoExit",
        "-Command",
        f"cd '{WORK_DIR}'; .\\{BAT_FILE}"
    ]
    
    print(f"[{get_timestamp()}] [*] 启动 webui...")
    process = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
    pid = process.pid
    save_pid(pid)
    print(f"[{get_timestamp()}] [✓] WebUI已启动，PID: {pid}")
    return pid

def kill_process_tree(pid):
    """强制杀死进程树"""
    try:
        subprocess.run(f"taskkill /F /T /PID {pid}", shell=True, capture_output=True)
        print(f"[{get_timestamp()}] [✓] 已杀死进程树: PID {pid}")
        return True
    except Exception as e:
        print(f"[{get_timestamp()}] [!] 杀死进程失败: {e}")
        return False

def check_file_status(monitor_folder, last_file_count, no_change_count):
    """检查文件状态 - 返回(新文件数, 无变化计数)"""
    current_file_count = get_file_count(monitor_folder)
    
    if current_file_count != last_file_count:
        print(f"[{get_timestamp()}] [✓] 文件数变化: {last_file_count} -> {current_file_count} (无变化计数重置为0)")
        return current_file_count, 0  # 有变化，重置计数
    else:
        no_change_count += 1
        print(f"[{get_timestamp()}] [!] 文件数未变化: {current_file_count} 个文件 (连续无变化: {no_change_count}/{MAX_NO_CHANGE_COUNT})")
        return last_file_count, no_change_count  # 无变化，计数+1

def check_and_restart_if_needed(pwsh_pid, monitor_folder, last_file_count, no_change_count):
    """检查文件变化，如果连续3次无变化则重启"""
    last_file_count, no_change_count = check_file_status(monitor_folder, last_file_count, no_change_count)
    
    # 检查是否达到3次无变化
    if no_change_count >= MAX_NO_CHANGE_COUNT:
        print(f"[{get_timestamp()}] [!] 文件连续{MAX_NO_CHANGE_COUNT}次无变化，执行重启流程...")
        kill_process_tree(pwsh_pid)
        print(f"[{get_timestamp()}] [*] 等待10秒，确保所有进程完全关闭...")
        time.sleep(10)
        print(f"[{get_timestamp()}] [*] 重启WebUI...")
        pwsh_pid = start_webui()
        print(f"[{get_timestamp()}] [*] 新启动WebUI，延迟120秒后开始文件监控...")
        time.sleep(120)
        no_change_count = 0  # 重置计数
        last_file_count = get_file_count(monitor_folder)  # 重新初始化文件数
    
    return pwsh_pid, no_change_count, last_file_count

def monitor():
    """监控逻辑"""
    print("\n" + "="*80)
    print(f"[{get_timestamp()}] 🚀 WebUI监控启动")
    print(f"[{get_timestamp()}] 📋 监控模式: {MONITOR_MODE.upper()}")
    print("="*80 + "\n")
    
    # 检查缓存中是否有PID
    cached_pid = load_pid()
    if cached_pid and pid_exists(cached_pid):
        print(f"[{get_timestamp()}] [✓] 发现缓存PID: {cached_pid}，进程仍存在，继续监控")
        pwsh_pid = cached_pid
        need_delay = False  # 缓存进程无需延迟
    else:
        print(f"[{get_timestamp()}] [*] 无有效缓存或进程已结束，启动新WebUI")
        pwsh_pid = start_webui()
        need_delay = True  # 新启动的进程需要延迟
    
    # 初始化文件计数
    monitor_folder = get_monitor_folder()
    no_change_count = 0  # 无变化计数器
    
    # 如果是新启动的进程，延迟2分钟后才开始计时
    if need_delay:
        print(f"[{get_timestamp()}] [*] 新启动WebUI，延迟120秒后开始文件监控...")
        time.sleep(120)
    
    last_file_count = get_file_count(monitor_folder)
    
    print(f"[{get_timestamp()}] [*] 监控文件夹: {monitor_folder}")
    print(f"[{get_timestamp()}] [*] 初始文件数: {last_file_count}")
    print(f"[{get_timestamp()}] [*] 检查间隔: {CHECK_INTERVAL}秒")
    print(f"[{get_timestamp()}] [*] 触发重启条件: 连续{MAX_NO_CHANGE_COUNT}次检查无新文件产生\n")
    
    try:
        while True:
            time.sleep(CHECK_INTERVAL)
            
            # 检查进程是否存在
            if not pid_exists(pwsh_pid):
                print(f"[{get_timestamp()}] [!] 进程 {pwsh_pid} 已结束，重启WebUI")
                pwsh_pid = start_webui()
                print(f"[{get_timestamp()}] [*] 新启动WebUI，延迟120秒后开始文件监控...")
                time.sleep(120)
                last_file_count = get_file_count(monitor_folder)
                no_change_count = 0  # 重置无变化计数
                continue
            
            # 根据模式获取监控文件夹 (WebUI模式每次都重新获取)
            monitor_folder = get_monitor_folder()
            
            # 检查队列和文件，决定是否重启
            pwsh_pid, no_change_count, last_file_count = check_and_restart_if_needed(pwsh_pid, monitor_folder, last_file_count, no_change_count)
    
    except KeyboardInterrupt:
        print(f"\n[{get_timestamp()}] [✓] 监控已停止")

if __name__ == "__main__":
    monitor()
