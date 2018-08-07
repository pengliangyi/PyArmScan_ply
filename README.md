# huago scanner

## 安装依赖

```bash
$ pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 运行 server

```bash
$ python server.py
```

## 运行 client

```bash
$ python client.py
```

## 开始扫描

在 client 端发送 “扫描” 命令：

```bash
# client
cmd> scan
OK
```

在 server 端看日志打印：

```bash
...
start to scan
...
```

## 手动触发生成 “生成图像” 的事件：

```bash
$ curl -i -H 'Content-Type: application/json' -XPOST http://localhost:5000/events -d '{"event": "gen_image"}'
```
