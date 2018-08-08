# PyArmScan

## 安装依赖

```bash
$ pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 运行 server

在板子上运行 server：

```bash
$ python server.py --port 5000
```

## 运行 client

在控制端（如 PC）上运行 client：

```bash
$ python client.py --port 5000
```

## 发送命令

发送 “扫描仪开机” 命令：

```bash
$ curl -i -H 'Content-Type: application/json' -XPOST http://localhost:5000/commands -d '{"command": "boot"}'
```

发送 “开始工作” 命令：

```bash
$ curl -i -H 'Content-Type: application/json' -XPOST http://localhost:5000/commands -d '{"command": "start"}'
```

## 手动触发事件

手动触发产生 “生成图像” 的事件：

```bash
$ curl -i -H 'Content-Type: application/json' -XPOST http://localhost:5000/events -d '{"event": "gen_image"}'
```
