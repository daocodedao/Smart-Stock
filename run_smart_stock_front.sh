#!/bin/bash
# 获取脚本所在目录
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
base_dir="$( cd "$script_dir" && pwd )"
echo "base_dir: $base_dir"
cd $base_dir


# 端口号
PORT=38889

# 查找占用指定端口的进程 ID
PID=$(lsof -ti :$PORT)

# 如果找到进程，则终止它
if [ -n "$PID" ]; then
  echo "Stopping process on port $PORT (PID: $PID)..."
  kill -9 $PID
  sleep 1 # 等待进程完全停止
else
  echo "No process found running on port $PORT."
fi

# 如果操作为 stop，则到此结束
if [ "$action" = "stop" ]; then
    echo "${GREEN}已完成停止操作${NOCOLOR}"
    exit 0
fi

# 否则继续启动服务
mkdir -p logs
logName="run_smart_stock_front"
echo "${YELLOW}nohup npm run dev -- --port $PORT > logs/${logName}.log 2>&1 &${NOCOLOR}"
nohup npm run dev -- --port $PORT > logs/${logName}.log 2>&1 &

echo ------Web服务已启动 请不要关闭------
echo 访问地址 : http://localhost:38888/
