[Gitee](https://gitee.com/haujet/jump-cutter-improved)　|　[Github](https://github.com/HaujetZhao/JumpCutter-Improved) 

## 💡 简介

### 名字由来

对 JumpCutter 进行改进。

原来 JumpCutter 需要把视频所有帧都提取成照片，存储在硬盘上，一段100多兆的视频，就可能产生20多G的图片文件，对硬盘寿命影响很大。

改进后使用标准输入和标准输出，数据都是经过内存，不再频繁读写硬盘。

结合了 pyav 多进程读取视频、subprocess ffmpeg 写视频，速度是 JumpCutter 的 2 到 3 倍多。

### 作用

它的作用是：对视频中的声音进行分析，分成静音部分和非静音部分，分别施加不同的速度，最后合成到一个新视频。

因为在许多种类的视频中，只有有声音的片段是人在说话的，其他安静的片段信息含量很少，就可以对静音部分加倍速，减少无用信息。比如将一个网课视频有声速度调为 1，静音速度调为 9999。

### 只处理音频

处理视频是比较花时间的，你可以选择只处理音频，听一下输出文件中音频的效果，再确定最终参数，最后输出视频。

### 辅助音频

此外，你可以给他添加一个辅助音频，用这个辅助音频来分片段。因为你的成品视频可能是包含背景音乐的，所以原视频中音频的背景音乐的音量会干扰分段。

有一个开源程序叫 Spleeter，它可以将视频中的人声和背景音分开，你就可以将人声提取出来作为辅助音频，处理原视频。

### Spleeter 生成辅助音频

Spleeter 可以将音频中的人声和背景声（音乐、风声、杂音）分开。如果你的视频的声音中，有大量杂音，影响自动分段，那就可以启用这个选项，脚本会先将音频声音中的背景音乐、杂音去掉，只留下纯净的人声，再进行分段变速。



## 🔮 使用方法

Windows 64 位用户，请直接到 release 界面找网盘链接，下载 7z 压缩包，解压后，双击 `运行.bat` 就可以用了。整个 7z 压缩包有 1GB，解压出来后有 2.3GB。体积这么大主要是因为里面塞了一个 tenserflow 引擎和一个 spleeter 模型。

其它系统的用户请从源码运行。

直接运行后，会有中文提示，按照提示设置输入文件等参数即可。



## 🛠 源码运行

请确保安装了 Python3.8 （spleeter 目前最高只支持 python3.8），你可以选择使用虚拟环境。

> 虚拟环境安装方法：
>
> ```
> # 先进入当前目录
> python -m venv .
> 
> # 对 Windows，切换到虚拟环境：
> .\Scripts\activate.bat
> ```

安装依赖前 Windows 用户需要安装微软运行库

安装依赖：

```
pip install av audiotsm spleeter
```

从 [spleeter](https://github.com/deezer/spleeter/releases) 下载 [5stems-finetune.tar.gz](https://github.com/deezer/spleeter/releases/download/v1.4.0/5stems-finetune.tar.gz) （训练好的模型），将其中的内容文件夹解压到 `src/pretrained_models/5stems` 文件夹中。

直接运行 `python __init__.py` ，会有中文提示，按照提示设置输入文件等参数即可。

或者 `python __init__.py 输入文件` 

或者  `python __init__.py 输入文件 输出文件` 

#### 二进制包

在音频变速部分，优先使用 [soundstretch](http://www.surina.net/soundtouch/soundstretch.html) ，这是一个 c 实现的开源的音频变速软件，可以不改变声调，对音频进行伸缩，许多知名项目都是用着它来进行音频变速。

但是它没有 python 实现，所以我只能调用他的二进制包。这个 repository 已经包含了 Windows 和 MacOS 的 soundstretch 二进制包。如果你想在其他系统上也用它来处理音频，请自行安装。

当然如果你没有安装 [soundstretch](http://www.surina.net/soundtouch/soundstretch.html) 的话，会使用次选方案 audiotsm 进行变速。但是它的变速效果有些差。

## ☕ 打赏

万水千山总是情，一块几块都是情。本软件完全开源，用爱发电，如果你愿意，可以以打赏的方式支持我一下：

<img src="src/misc/sponsor.jpg" alt="sponsor" style="zoom:50%;" />



## 😀 交流

如果有软件方面的反馈可以提交 issues，或者加入 QQ 群：[1146626791](https://qm.qq.com/cgi-bin/qm/qr?k=DgiFh5cclAElnELH4mOxqWUBxReyEVpm&jump_from=webapi) 