# 行情播报微信机器人

[![Powered by Wechaty](https://img.shields.io/badge/Powered%20By-Wechaty-green.svg)](https://github.com/chatie/wechaty)
[![Wechaty开源激励计划](https://img.shields.io/badge/Wechaty-开源激励计划-green.svg)](https://github.com/juzibot/Welcome/wiki/Everything-about-Wechaty)

使用Wechaty开发的行情播报微信机器人，为微信群组用户提供实时行情信息播报服务。

## 运行Wechaty Hostie服务

### 准备工作

准备一台服务器，具备以下条件：

1. 公开IP：可通过互联网访问；
2. 公开端口：可通过互联网访问；
3. Docker。

### 运行步骤

#### 1. 安装Wechaty的Docker镜像

```sh
docker pull zixia/wechaty
```

#### 2. 设置`wechaty-puppet-hostie`

可使用自定义的随机字符串

```sh
export WECHATY_TOKEN=puppet_hostie_your_token
```

#### 3. 开启Wechaty Puppet服务

```sh
export WECHATY_HOSTIE_PORT=8888
export WECHATY_PUPPET=wechaty-puppet-padplus
export WECHATY_PUPPET_PADPLUS_TOKEN=puppet_padplus_token
export WECHATY_LOG=verbose

docker run \
  --rm \
  -ti \
  -e WECHATY_LOG="$WECHATY_LOG" \
  -e WECHATY_PUPPET="$WECHATY_PUPPET" \
  -e WECHATY_HOSTIE_PORT="$WECHATY_HOSTIE_PORT" \
  -e WECHATY_TOKEN="$WECHATY_TOKEN" \
  -e WECHATY_PUPPET_PADPLUS_TOKEN="$WECHATY_PUPPET_PADPLUS_TOKEN" \
  -p "$WECHATY_HOSTIE_PORT:$WECHATY_HOSTIE_PORT" \
  zixia/wechaty
```

#### 4. 检查Wechaty Puppet服务是否正常开启

访问`https://api.chatie.io/v0/hosties/TOKEN`，其中`TOKEN`为前面设置的`WECHATY_TOKEN`。如果返回结果中包含前面设置的IP和端口，则服务正常开启。如果返回结果为：

```
{"ip":"0.0.0.0","port":0}
```

则服务没有正常开启，需要按照上面的步骤重新检查。

## 运行行情播报微信机器人

### 下载源码

从github代码库中克隆源代码

```sh
git clone https://github.com/exctech/market-wechat-robot.git
```

### 运行机器人

```sh
python market-robot.py
```