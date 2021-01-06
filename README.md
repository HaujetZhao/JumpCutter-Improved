[Gitee](https://gitee.com/haujet/jump-cutter-improved)　|　[Github](https://github.com/HaujetZhao/JumpCutter-Improved) 

## 简介

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

如果你的电脑上安装了 Spleeter，并且下载了 Spleeter 的模型库，请编辑源代码中的下列部分：

```python
class Parameters():
    def __init__(self):
        ........
        self.spleeter的Python解释器路径 = 'D:/虚拟环境/Spleeter/Scripts/python.exe'
        self.spleeter的模型文件夹路径 = 'D:/pretrained_models'
        self.使用spleeter生成辅助音频 = False
        self.spleeter使用模型名称 = '5stems'
        self.spleeter辅助音频文件名 = 'vocals.wav'
        self.spleeter调用命令行 = True  # 如果改成 False，就会在本脚本内调用 spleeter 模块，但是 Windows 下调用 spleeter 不能使用多线程，速度会慢些。所以建议使用命令行的方式调用 Spleeter。

```

将可以运行 Spleeter 的 python 解释器路径、Spleeter的模型文件夹路径填入对应的位置，脚本在检测到 Spleeter 可用之后，在运行时会提示是否启用。

如果上述参数填写不正确，或者 Spleeter 没有安装上，那么这个选项会默认禁用。

Spleeter 对一些依赖包有版本要求，用 pip 安装时，可能将电脑上的一些包替换成更旧的版本，所以建议使用 Python 虚拟环境：

* 新建一个目录，在这个目录下，运行 `python -m venv .` 就可以将这个目录初始化为一个虚拟环境了
* 再执行 `scripts/activate.bat` 就激活进入这个虚拟环境了，在这个环境下，使用 `pip install spleeter` 就可以放心地将 spleeter 安装到这个虚拟环境中
* 找到这个环境中的 `python.exe` 文件，它就是能够运行spleeter的Python解释器，将其路径填入源码。
* 从 [spleeter releases](https://github.com/deezer/spleeter/releases) 界面下载一个训练好的模型，解压到一个文件夹。模型的父目录应该是名为 `pretrained_models`，比如五音轨模型的目录就应该是 `pretrained_models/5stems` 



## 使用方法

直接运行 `python __init__.py` ，会有中文提示，按照提示设置输入文件等参数即可。

或者 `python __init__.py 输入文件` 

或者  `python __init__.py 输入文件 输出文件` 

## 依赖

#### Python 依赖：

```
av
numpy
scipy
audiotsm
```

#### 二进制包

在音频变速部分，优先使用 [soundstretch](http://www.surina.net/soundtouch/soundstretch.html) ，这是一个 c 实现的开源的音频变速软件，可以不改变声调，对音频进行伸缩，许多知名项目都是用着它来进行音频变速。

但是它没有 python 实现，所以我只能调用他的二进制包。这个 repository 已经包含了 Windows 的 soundstretch 二进制包。如果你想在其他系统上也用它来处理音频，请自行安装。

当然如果你没有安装 [soundstretch](http://www.surina.net/soundtouch/soundstretch.html) 的话，会使用次选方案 audiotsm 进行变速。但是它的变速效果有些差。


