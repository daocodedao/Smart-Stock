# 项目介绍
## 使用文档
[Smart-Stock使用指南](https://smart-stock-docs.readthedocs.io/en/latest/index.html)
## 1 项目概述
Smart-Stock可以是一个复盘及量化策略回测的项目，初衷是利用开源数据做一个开源的项目，用于学习和研究。虽然市面上有很多回测的网站，但大多长期使用需要收费且个人用户一般很难获得可以本地开发调试的SDK，且需要熟悉api接口有一定学习成本。Smart-Stock是一个完全利用开源工具搭建的回测系统，目前只支持A股股票数据分析和回测。
## 2 系统架构图
理想中结构图如下所示，该仓模型预测部分暂时不支持。
![alt text](./docs/imgs/design.jpg)


## 使用
### 数据库
```

CREATE DATABASE smart_stock
CHARACTER SET utf8mb4
COLLATE utf8mb4_general_ci;

```


### 环境搭建
```
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt 

```
### 修改 qstock
```
vim venv/lib/python3.10/site-packages/qstock/data/util.py

- from py_mini_racer import py_mini_racer
+ from py_mini_racer import MiniRacer

- js_code = py_mini_racer.MiniRacer()
+ js_code = MiniRacer()

vim venv/lib/python3.10/site-packages/qstock/data/money.py
- from py_mini_racer import py_mini_racer
+ from py_mini_racer import MiniRacer

- js_code = py_mini_racer.MiniRacer()
+ js_code = MiniRacer()

# 手动安装
pip install mini-racer
pip install pyfolio

```

### 后端服务
安装成功后可通过以下命令启动后端服务
```
python src/web/smart_stock_backend.py --host 0.0.0.0 --port 38888
# 参数说明
    --host 指定服务绑定的ip
    --port 指定服务绑定的端口
```

### 前端服务
## 3 前端环境搭建
克隆代码
```
git clone https://github.com/Reyn-AI/Smart-Stock-Web.git
cd Smart-Stock-Web/
```
运行服务
```
## 安装vue3环境
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
npm init vite@latest
## 安装运行环境
npm i
## 修改后端服务ip和端口
vim .env
    VITE_SERVER_IP=xxx.xxx.xxx.xxx
    VITE_SERVER_PORT=xxxxx
## 启动服务
npm run dev -- --port 38889

```


### frp
```
cat /data/work/frp/frpc.ini 
vim /data/work/frp/frpc.ini

# gradio_university 6610
[ssh-SmartStock38888]
type = tcp
local_ip = 127.0.0.1
local_port = 38888
remote_port = 38888
use_encryption = false
use_compression = false

[ssh-SmartStock38889]
type = tcp
local_ip = 127.0.0.1
local_port = 38889
remote_port = 38889
use_encryption = false
use_compression = false

# 重启frp
sudo systemctl restart  supervisor
sudo supervisorctl reload
sudo supervisord
```