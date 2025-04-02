#!/bin/bash

mkdir -p /data/work/mongo/config
mkdir -p /data/work/mongo/data
mkdir -p /data/work/mongo/logs
touch /data/work/mongo/config/mongod.conf
chmod 777 /data/work/mongo

# vim /data/work/mongo/config/mongod.conf

# # 数据库存储路径
# dbpath=/data/work/mongo/data
# # 日志文件路径
# logpath=/data/work/mongo/logs/mongod.log
# # 监听的端口
# port=27017
# # 允许所有的 IP 地址连接
# bind_ip=0.0.0.0
# # 启用日志记录
# journal=true
# # 是否后台运行
# fork=true
# # 启用身份验证
# auth=true


docker run -itd --name mongo -p 27017:27017 -v /data/work/mongo/config/mongod.conf:/etc/mongod.conf \
           -v /data/work/mongo/data:/data/db \
           -v /data/work/mongo/logs:/var/log/mongodb \
           -e MONGO_INITDB_ROOT_USERNAME=admin \
           -e MONGO_INITDB_ROOT_PASSWORD=iShehui2021! \
           --restart=always mongo