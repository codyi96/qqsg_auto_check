## 使用
### 1. 安装[chromedriver](http://chromedriver.storage.googleapis.com/index.html)
* 需要使用chrome浏览器
* 需要安装浏览器对应版本的chrome driver, 如何安装自行百度

### 2. 安装python和pip

### 3. 依赖包
```bash
pip install selenium
pip install opencv-python
```
### 4.配置config.json
将user1 password1改成自己的账号, 多个账号自行修改配置文件
```json
{
    "users": [
        {
            "u": "user1",
            "p": "password1"
        }
    ]
}
```
### 5.运行
```bash
python check_in.py
```
## 参考
* [滑块验证](https://github.com/wkunzhi/Python3-Spider/tree/master/%E6%BB%91%E5%8A%A8%E9%AA%8C%E8%AF%81%E7%A0%81/%E3%80%90%E8%85%BE%E8%AE%AF%E3%80%91%E6%BB%91%E5%9D%97%E9%AA%8C%E8%AF%81)