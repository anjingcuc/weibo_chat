# 微博私信导出工具

一个简陋但是能用的微博私信导出工具，仅支持导出单个对话，导出后文本聊天记录会存放在 `chat.txt` 中，语音、图片、视频会按照时间命名放在同一文件夹下。

## 依赖

安装 Python 环境。自行安装 Chrome 浏览器并下载对应版本的 chromedriver 并将 chromedriver 所在目录放在环境变量中。

```bash
pip install selenium
pip install requests
```

## 运行

安装好以上环境后:

```bash
python weibo_chat.py
```

在弹出的浏览器中扫码登录微博，页面会自动跳转到私信聊天页面，默认获取最顶部的对话。