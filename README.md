## WechatTools
这是利用itchat和pyqt5实现的一个微信工具集合小软件，具有好友分析，~~好友删除检测~~，消息防撤回，自动聊天机器人等功能。

### 使用前必读
- WechatTools使用的itchat库采用的网页微信登录接口，请勿长时间在线，建议每次登录时长不要超过12小时，否则可能会被腾讯限制网页微信登录功能。
- 因为采用的网页微信登录，所以不能和电脑微信同时在线。
- 使用前请保证已连接互联网，否则软件会自动退出。
- 本软件仅用于交流学习，不当使用造成的一切后果与作者无关。

### 功能简介
#### 1. 好友分析
好友分析会会生成三张图表，分别是：
- 好友数量与性别比例图
- 好友地区分布图
- 以用户自己的微信头像为背景的好友微信个性签名云图


**性别比例图：**

![image](http://pcz102fvz.bkt.clouddn.com/sex_analysis.png)


**地区分布图：**

![image](http://pcz102fvz.bkt.clouddn.com/area_analysis.png)

**个性签名云图：**

![image](http://pcz102fvz.bkt.clouddn.com/cloud.png)
#### 2. 好友删除检测
原理为邀请好友进入群聊，非好友和黑名单用户无法邀请，由于现在微限制信邀请好友的频率，该功能已经无法使用。

#### 3. 消息防撤回
消息防撤回功能可以将所有聊天中（包含群聊）撤回的消息和文件保存至本地，同时将消息和文件通过文件传输助手传送至用户手机。

**消息撤回演示：**

![image](http://pcz102fvz.bkt.clouddn.com/withdraw_msg.png)

**消息撤回保存的本地文件：**

![image](http://pcz102fvz.bkt.clouddn.com/withdraw_file.png)

**消息撤回通过文件助手发送给手机：**

![image](http://pcz102fvz.bkt.clouddn.com/withdraw_mobi.png)


#### 4. 自动聊天机器人
将个人微信变成AI机器人，自动回复文字消息。再也不用担心女朋友的骚扰（手动滑稽），只是聊分手的话请收好你的40米大刀，谢谢合作O(∩_∩)O。
为了防止造成骚扰，暂时只支持个人好友的消息回复，群聊消息不支持回复。

**自动聊天机器人演示：**

![image](http://pcz102fvz.bkt.clouddn.com/auto_reply.png)