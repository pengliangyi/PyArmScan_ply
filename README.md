# PyArmScan

## 安装依赖

```bash
$ pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 运行 server

在板子上运行 server：

```bash
$ python server.py
```

## 运行 client

在控制端（如 PC）上运行 client：

```bash
$ python client.py
```

## 开始扫描

在 client 端发送 “开始” 命令：

```bash
# client
cmd> start
OK
```

## 手动触发 “生成图像” 的事件：

```bash
$ curl -i -H 'Content-Type: application/json' -XPOST http://localhost:5000/events -d '{"event": "gen_image"}'
```
