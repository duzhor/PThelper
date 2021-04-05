# PThelper

# 安装

本脚本支持将执行结果推送至 [pushplus](https://pushplus.hxtrip.com/ "pushplus")

本脚本依赖于python3，请先建立好运行环境

```
# RedHat/CentOS
yum install -y python3 python3-devel python3-pip
python3 -m pip install -U pip setuptools
```

```
# Debian/Ubuntu
apt install -y python3 python3-dev python3-pip
python3 -m pip install -U pip setuptools
```


此处定义脚本路径为 `~/PThelper`
```
# 创建独立的python虚拟环境
cd ~/PThelper
python3 -m venv env

# 激活venv虚拟环境
source ./env/bin/activate

# 安装脚本依赖
pip install -U pip setuptools
pip install -r requirements.txt
```

# 使用

复制 `config.yaml.example` 重命名为 `config.yaml`

编辑 `config.yaml`文件：

  修改 `TOKEN` 值为 [pushplus](https://pushplus.hxtrip.com/ "pushplus") 的 token

  修改 想要执行签到任务的站点cookie

```
# 手动执行
cd ~/PThelper && ~/PThelper/env/bin/python attendance.py
```

```
# 定时任务：每天08:30执行脚本
30 8 * * * cd ~/PThelper && ~/PThelper/env/bin/python attendance.py
```
