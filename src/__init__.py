# -*- coding: UTF-8 -*-
import av
import io
import math
import os
import platform
import pathlib
import re
import json
import subprocess
import sys
import tempfile
import threading
import time
from shutil import rmtree, copy

import numpy as np
from audiotsm import phasevocoder
from audiotsm.io.wav import WavReader, WavWriter
# from audiotsm2 import phasevocoder
# from audiotsm2.io.array import ArrReader, ArrWriter
from scipy.io import wavfile


os.chdir(os.path.dirname(os.path.abspath(__file__)))  # 更改工作目录，指向正确的当前文件夹
sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # 将当前目录导入 python 寻找 package 和 moduel 的变量
os.environ['PATH'] += os.pathsep + os.path.abspath('./bin/Windows')  # 将可执行文件的目录加入环境变量
os.environ['PATH'] += os.pathsep + os.path.abspath('./bin/MacOS')  # 将可执行文件的目录加入环境变量

class Parameters():
    def __init__(self):
        self.输入文件 = ''
        self.输出文件 = ''

        self.静音片段速度 = 4.00
        self.有声片段速度 = 1.00

        self.片段间缓冲帧数 = 3
        self.声音检测相对阈值 = 0.04

        self.视频编码器 = 'libx264'
        self.视频质量crf参数 = 23

        self.只处理音频 = False
        self.辅助音频文件 = ''


        # 音频淡入淡出大小，使声音在不同片段之间平滑
        self.音频过渡区块大小 = 400

        self.临时文件夹 = ''
        self.出错存放文件夹 = ''

        self.临时数据 = None

        self.spleeter的Python解释器路径 = 'python'
        self.spleeter的模型文件夹路径 = (pathlib.Path('.').resolve() / 'pretrained_models').as_posix()
        self.使用spleeter生成辅助音频 = True
        self.spleeter使用模型名称 = '5stems'
        self.spleeter辅助音频文件名 = 'vocal.wav'
        self.spleeter调用命令行 = False  # 如果改成 False，就会在本脚本内调用 spleeter 模块，但是 Windows 下调用 spleeter 不能使用多线程，速度会慢些。所以建议使用命令行的方式调用 Spleeter。
        self.separator = None

    # @profile()
    def 得到参数(self):
        self.得到输入文件()
        self.得到输出文件()

        self.得到静音片段速度()
        self.得到有声片段速度()

        # self.得到片段间缓冲帧数()
        # self.得到声音检测相对阈值()
        #
        # self.得到视频编码器()
        # self.得到视频质量crf参数()
        #
        # self.得到只处理音频()
        # self.得到辅助音频文件()
        #
        # self.得到使用spleeter生成辅助音频()

        self.确认参数()

        self.检查目标文件路径(self.输出文件)
        self.得到临时文件夹()

    def 确认参数(self):
        用户输入 = input(f'''\n得到以下处理参数：\n
    1. 输入文件：{self.输入文件}
    2. 输出文件：{self.输出文件}\n
    3. 静音片段速度：{self.静音片段速度}
    4. 有声片段速度：{self.有声片段速度}\n
    5. 片段间缓冲帧数：{self.片段间缓冲帧数}
    6. 声音检测相对阈值：{self.声音检测相对阈值}\n
    7. 视频编码器：{self.视频编码器}
    8. 视频质量crf参数：{self.视频质量crf参数}\n
    9. 只处理音频：{self.只处理音频}
   10. 辅助音频文件：{self.辅助音频文件}\n
   11. 使用 spleeter 生成辅助音频文件：{self.使用spleeter生成辅助音频}\n
如果确认正确，请回车继续，接下来将开始视频处理；
而如果有参数不正确，需要修改，请输入对应的序号，再回车：\n\n''')
        try:
            if 用户输入 == '':
                return
            else:
                int(用户输入)
        except:
            return
        if int(用户输入) == 1:
            self.得到输入文件()
        elif int(用户输入) == 2:
            self.得到输出文件()

        elif int(用户输入) == 3:
            self.得到静音片段速度()
        elif int(用户输入) == 4:
            self.得到有声片段速度()

        elif int(用户输入) == 5:
            self.得到片段间缓冲帧数()
        elif int(用户输入) == 6:
            self.得到声音检测相对阈值()

        elif int(用户输入) == 7:
            self.得到视频编码器()
        elif int(用户输入) == 8:
            self.得到视频质量crf参数()

        elif int(用户输入) == 9:
            self.得到只处理音频()
        elif int(用户输入) == 10:
            self.得到辅助音频文件()
        elif int(用户输入) == 11:
            self.得到使用spleeter生成辅助音频()
        else:
            return
        self.确认参数()

    def 得到输入文件(self):
        if len(sys.argv) > 1 and self.输入文件 == '' and os.path.exists(sys.argv[1]):
            self.输入文件 = sys.argv[1]
            print(f'要处理的视频文件为：{self.输入文件}')

        else:
            while True:
                用户输入 = input(f'请输入要处理的视频路径：\n    (默认值：{self.输入文件})\n')
                if 用户输入 == '':
                    if self.输入文件 != '':
                        break
                if os.path.exists(用户输入.strip('\'"')):
                    self.输入文件 = 用户输入.strip('\'"')
                    break
                else:
                    print('输入的文件不存在，请重新输入')

    def 得到输出文件(self):
        if self.输出文件 == '':
            if len(sys.argv) > 2:
                self.输出文件 = sys.argv[2]
            else:
                输入文件Path = pathlib.Path(self.输入文件)
                self.输出文件 = (输入文件Path.parent / (输入文件Path.stem + '-剪辑后' + 输入文件Path.suffix)).as_posix()
        用户输入 = input(f'\n输出文件的路径被设为：\n    {self.输出文件}\n    如果接受，请回车跳过，如果要修改输出路径，请输入：\n')
        if 用户输入 != '':
            self.输出文件 = 用户输入.strip('\'"')

    def 得到静音片段速度(self):
        self.静音片段速度 = self.得到小数(f'\n请输入静音片段速度：', self.静音片段速度, 0.10, 9999999999999999)

    def 得到有声片段速度(self):
        self.有声片段速度 = self.得到小数(f'\n请输入有声片段速度：', self.有声片段速度, 0.10, 9999999999999999)

    def 得到片段间缓冲帧数(self):
        self.片段间缓冲帧数 = self.得到整数(f'\n请输入片段间缓冲帧数：', self.片段间缓冲帧数, 0, 30)

    def 得到声音检测相对阈值(self):
        self.声音检测相对阈值 = self.得到小数(f'\n请输入声音检测相对阈值：', self.声音检测相对阈值, 0.0, 1.0)

    def 得到视频编码器(self):
        self.视频编码器 = self.得到字符串(f'\n请输入视频编码器：\n    libx264 速度快\n    libx265 体积小', self.视频编码器)

    def 得到视频质量crf参数(self):
        self.视频质量crf参数 = self.得到整数(f'\n请输入视频质量crf参数，越低画质越好，同时体积越大：', self.视频质量crf参数, 0, 51)

    def 得到只处理音频(self):
        self.只处理音频 = self.得到布尔值(f'\n请输入是否只处理音频，如果是的话，会忽略处理视频。', self.只处理音频)

    def 得到辅助音频文件(self):
        while True:
            self.辅助音频文件 = self.得到字符串('\n如果有辅助音频（比如去除了背景音的音频轨），你可以在这里输入，直接回车表示为空', '').strip('\'"')
            if self.辅助音频文件 != '' and not os.path.exists(self.辅助音频文件):
                print(f'您输入的音频文件路径不存在，请重新输入')
                continue
            break

    def 得到使用spleeter生成辅助音频(self):
        if self.spleeter调用命令行:
            if os.path.exists(self.spleeter的Python解释器路径) and os.path.exists(self.spleeter的模型文件夹路径) and pathlib.Path(
                    self.spleeter的模型文件夹路径).name == 'pretrained_models':
                self.使用spleeter生成辅助音频 = self.得到布尔值(f'''\n是否使用 spleeter 生成辅助音频文件用于分段？
    spleeter的Python解释器路径：{self.spleeter的Python解释器路径}
    spleeter的模型文件夹路径：{self.spleeter的模型文件夹路径}
    spleeter 使用的模型名称：{self.spleeter使用模型名称}
    spleeter 辅助音轨名：{self.spleeter辅助音频文件名}\n''', self.使用spleeter生成辅助音频)
            else:
                self.使用spleeter生成辅助音频 = False
        else:
            self.使用spleeter生成辅助音频 = self.得到布尔值('\n是否使用 spleeter 生成辅助音频文件用于分段？', self.使用spleeter生成辅助音频)


    def 检查目标文件路径(self, 路径):
        目标文件夹Path = pathlib.Path('路径').parent
        if not 目标文件夹Path.exists():
            目标文件夹Path.mkdir(parents=True)
    def 清空separator(self):
        del self.separator

    def 清空临时数据(self):
        del self.临时数据
        self.临时数据 = None

    def 得到临时文件夹(self):
        self.临时文件夹 = tempfile.mkdtemp(dir=os.path.dirname(self.输出文件), prefix=pathlib.Path(self.输入文件).stem)
        self.出错存放文件夹 = tempfile.mkdtemp(dir=self.临时文件夹, prefix='出错文件')

    def 得到整数(self, 提示语, 默认值: int, 最小值: int, 最大值: int):
        while True:
            数值 = input(提示语 + f'\n    (默认值：{默认值}   有效数值：{最小值} ~ {最大值})\n')
            if 数值 == '':
                return 默认值
            try:
                数值 = int(数值)
            except:
                print('您的输入不是有效数字，请重新输入')
                continue
            if 数值 < 最小值 or 数值 > 最大值:
                print('您输入的值不在有效范围内，请重新输入')
                continue
            break
        return 数值

    def 得到小数(self, 提示语, 默认值: float, 最小值: float, 最大值: float):
        while True:
            数值 = input(提示语 + f'\n    (默认值：{默认值}   有效数值：{最小值} ~ {最大值})\n')
            if 数值 == '':
                return 默认值
            try:
                数值 = float(数值)
            except:
                print('您的输入不是有效数字，请重新输入')
                continue
            if 数值 < 最小值 or 数值 > 最大值:
                print('您输入的值不在有效范围内，请重新输入')
                continue
            break
        return 数值

    def 得到字符串(self, 提示语, 默认值: str):
        数值 = input(提示语 + f'\n    (默认值：{默认值})\n')
        if 数值 == '':
            return 默认值
        return 数值

    def 得到布尔值(self, 提示语, 默认值: bool):
        用户回应 = input(提示语 + f'\n    (默认值：{默认值})\n    输入 1、y、True 表示“是”；输入 0, n, False 或表示“否”；其它值或直接回车为默认\n').lower()
        if 用户回应 == '1' or 用户回应 == 'y' or 用户回应 == 'true':
            return True
        elif 用户回应 == '0' or 用户回应 == 'n' or 用户回应 == 'false':
            return False
        else:
            return 默认值

# @profile()
def 得到输入视频时长(视频文件):
    command = f'ffmpeg -hide_banner -i "{视频文件}"'
    进程 = subprocess.run(command, encoding='utf-8', capture_output=True)
    params = 进程.stderr
    del 进程
    m = re.search(r'Duration.+(\d{2}:\d{2}:\d{2}.\d{2}).+\n\s+Stream #.*Video.* ([0-9\.]*) fps', params)
    if m is not None:
        长度split = m.group(1).split(':')
        视频长度 = int(长度split[0]) * 60 * 60 + int(长度split[1]) * 60 + float(长度split[2])
        # print(f'视频长度是：{视频长度}')
        return 视频长度

def 得到输入视频帧率(视频文件):
    command = f'ffmpeg -hide_banner -i "{视频文件}"'
    进程 = subprocess.run(command, encoding='utf-8', capture_output=True)
    params = 进程.stderr.split('\n')
    del 进程
    for line in params:
        m = re.search(r'Stream #.*Video.* ([0-9\.]*) fps', line)
        if m is not None:
            视频帧率 = float(m.group(1))
            print(f'\n视频帧率是：{视频帧率}')
            return 视频帧率


def 得到输入音频采样率(音频文件):
    command = f'ffmpeg -hide_banner -i "{音频文件}"'
    进程 = subprocess.run(command, encoding='utf-8', capture_output=True)
    params = 进程.stderr.split('\n')
    del 进程
    for line in params:
        m = re.search('Stream #.*Audio.* ([0-9]*) Hz', line)
        if m is not None:
            采样率 = int(m.group(1))
            print(f'\n音频采样率是：{采样率}')
            return 采样率
    return

def 提取音频流(输入文件, 输出文件, 音频采样率):
    command = f'ffmpeg -hide_banner -i "{输入文件}" -ac 2 -ar {音频采样率} -vn "{输出文件}"'
    进程 = subprocess.run(command, stderr=subprocess.PIPE)
    del 进程
    return


def 得到最大音量(音频数据):
    maxv = float(np.max(音频数据))
    minv = float(np.min(音频数据))
    return max(maxv, -minv)


def 由音频得到片段列表(音频文件, 视频帧率, 参数: Parameters):
    # 变量 音频采样率, 总音频数据 ，得到采样总数为 wavfile.read("audio.wav").shape[0] ，（shape[1] 是声道数）
    采样率, 总音频数据 = wavfile.read(音频文件, mmap=True)
    总音频采样数 = 总音频数据.shape[0]

    最大音量 = 得到最大音量(总音频数据)
    if 最大音量 == 0: 最大音量 = 1
    每帧采样数 = 采样率 / 视频帧率
    总音频帧数 = int(math.ceil(总音频采样数 / 每帧采样数))
    hasLoudAudio = np.zeros((总音频帧数))

    # 这里给每一帧音频标记上是否超过阈值
    for i in range(总音频帧数):
        该帧音频起始 = int(i * 每帧采样数)
        该帧音频结束 = min(int((i + 1) * 每帧采样数), 总音频采样数)
        单帧音频区间 = 总音频数据[该帧音频起始:该帧音频结束]
        单帧音频最大相对音量 = float(得到最大音量(单帧音频区间)) / 最大音量
        if 单帧音频最大相对音量 >= 参数.声音检测相对阈值:
            hasLoudAudio[i] = 1

    # 按声音阈值划分片段
    片段列表 = [[0, 0, 0]]
    shouldIncludeFrame = np.zeros((总音频帧数))  # 返回一个数量为 音频总帧数 的列表，默认数值为0，用于存储是否该存储这一帧
    for i in range(总音频帧数):
        start = int(max(0, i - 参数.片段间缓冲帧数))
        end = int(min(总音频帧数, i + 1 + 参数.片段间缓冲帧数))
        # 如果从加上淡入淡出的起始到最后之间的几帧中，有1帧是要保留的，那就保留这一区间所有的
        shouldIncludeFrame[i] = np.max(hasLoudAudio[start:end])
        # 如果这一帧不是总数第一帧 且 是否保留这一帧 与 前一帧 不同
        if (i >= 1 and shouldIncludeFrame[i] != shouldIncludeFrame[i - 1]):  # Did we flip?
            片段列表.append([片段列表[-1][1], i, int(shouldIncludeFrame[i - 1])])
    片段列表.append([片段列表[-1][1], 总音频帧数, int(shouldIncludeFrame[i - 1])])  # 加一个最后那几帧要不要保留
    片段列表.pop(0)  # 把片段列表中开头那个开始用于占位的 [0,0,0]去掉
    print(f'静音、响亮片段分析完成')
    return 片段列表


def 打印列表(列表):...
    # print(f'列表信息如下：')
    # for i in range(len(列表)):
    #     print(f'{列表[i]}', end='    ')


def 查找可执行程序(program):
    """
    Return the path for a given executable.
    """

    def is_exe(file_path):
        """
        Checks whether a file is executable.
        """
        return os.path.isfile(file_path) and os.access(file_path, os.X_OK)

    fpath, _ = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            import platform
            if platform.system() == 'Windows':
                exe_file += '.exe'
            if is_exe(exe_file):
                return exe_file

# @profile()
def 由spleeter得到辅助音频数据(音频文件, 参数: Parameters, 模型父文件夹):
    if 参数.spleeter调用命令行:
        输入 = 音频文件
        输出 = 参数.临时文件夹
        wav文件Path = pathlib.Path(输出) / pathlib.Path(输入).stem / 参数.spleeter辅助音频文件名
        命令 = f'"{参数.spleeter的Python解释器路径}" -m spleeter separate -i "{输入}" -p spleeter:{参数.spleeter使用模型名称} -o "{输出}"'
        print('正在使用 spleeter 命令行参数分离音轨')
        进程 = subprocess.run(命令, cwd=模型父文件夹)
        del 进程
        time.sleep(1)
        采样率, 参数.临时数据 = wavfile.read(wav文件Path)
    else:

        print('\n正在使用 spleeter 分离音轨\n')
        # separator = Separator('spleeter:5stems', multiprocess=False)
        参数.separator.separate_to_file(音频文件, (pathlib.Path(参数.临时文件夹)).as_posix())
        采样率, 参数.临时数据 = wavfile.read((pathlib.Path(参数.临时文件夹)/pathlib.Path(音频文件).stem/'vocals.wav').as_posix())
        rmtree((pathlib.Path(参数.临时文件夹)/pathlib.Path(音频文件).stem).as_posix())
    return 采样率

# @profile()
def 由spleeter得到分析音频(输入文件, 输出文件, 参数: Parameters):
    开始时间 = time.time()
    片段时长 = 200

    # 这里使用 Memory Mapped File，无需将音频文件读取到内存
    # 避免了读取几个小时的长音频的时候，内存爆满
    采样率, 总音频数据 = wavfile.read(输入文件, mmap=True)

    长度 = len(总音频数据)
    时间 = 长度 / 采样率

    模型父文件夹 = (pathlib.Path(参数.spleeter的模型文件夹路径).resolve().parent).as_posix()


    if not 参数.spleeter调用命令行:
        from spleeter.separator import Separator
        os.chdir(模型父文件夹)
        参数.separator = Separator('spleeter:5stems', multiprocess=False)

    if 时间 > 片段时长:
        片段路径列表 = []
        片段数 = math.ceil(时间 / 片段时长)
        print(f'\n总音频时长为 {时间} 秒，超过了 {片段时长} 秒，需要分成 {片段数} 段依次处理')

        输入文件Path = pathlib.Path(输入文件)
        片段路径前缀 = (输入文件Path.parent / (输入文件Path.stem)).as_posix()

        index = 0
        for i in range(片段数):
            print(f'\n总共有 {片段数} 个音频片段需要处理，正在处理第 {i + 1} 个...')
        #     i = 0
            start = index
            index = end = min(index + (片段时长 * 采样率), 长度 - 1)

            片段数据 = 总音频数据[start:end]
            片段名字 = 片段路径前缀 + str(i + 1) + 输入文件Path.suffix
            片段路径列表.append(片段名字)
            wavfile.write(片段名字, 采样率, 片段数据)
            新采样率 = 由spleeter得到辅助音频数据(片段名字, 参数, 模型父文件夹)
            wavfile.write(片段名字, 新采样率, 参数.临时数据)
            参数.清空临时数据()
        音频片段合并(片段路径列表, 输出文件)

    else:
        print(f'\n总音频时长为 {时间} 秒，未超过 {片段时长} 秒，无需分段，直接处理')
        新采样率 = 由spleeter得到辅助音频数据(输入文件, 参数, 模型父文件夹)
        wavfile.write(输出文件, 新采样率, 参数.临时数据)
        参数.清空临时数据()
    参数.清空separator()
    if not 参数.spleeter调用命令行:
        del Separator
    print(f'\nSpleeter 耗时：{秒数转时分秒(time.time() - 开始时间)}\n')
    return

def 音频片段合并(片段列表:list, 输出文件:str):
    # 建立一个临时TXT文件，用于CONCAT记录
    concat文件夹 = (pathlib.Path(片段列表[0]).parent).as_posix()
    fd, concat文件 = tempfile.mkstemp(dir=concat文件夹, prefix='音频文件concat记录-', suffix='.txt')
    os.close(fd)

    # 将音频片段的名字写入CONCAT文件
    with open(concat文件, 'w', encoding='utf-8') as f:
        for 片段路径 in 片段列表:
            f.write(f'file {pathlib.Path(片段路径).name}\n')

    # FFMPEG连接音频片段
    command = f'ffmpeg -y -hide_banner -safe 0  -f concat -i "{concat文件}" -c:a copy "{输出文件}"'
    # print(command)
    进程 = subprocess.run(command, encoding='utf-8', cwd=concat文件夹, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    del 进程
    return


def 音频变速(wav音频数据列表, 声道数, 采样率, 目标速度):
    if 目标速度 == 1.0:
        return wav音频数据列表
    if 查找可执行程序('soundstretch') != None:
        内存音频二进制缓存区 = io.BytesIO()
        fd, soundstretch临时输出文件 = tempfile.mkstemp()
        os.close(fd)
        wavfile.write(内存音频二进制缓存区, 采样率, wav音频数据列表)
        变速命令 = f'soundstretch stdin "{soundstretch临时输出文件}" -tempo={(目标速度 - 1) * 100}'
        变速线程 = subprocess.Popen(变速命令, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        变速线程.communicate(内存音频二进制缓存区.getvalue())
        try:
            采样率, 音频区间处理后的数据 = wavfile.read(soundstretch临时输出文件)
        except Exception as e:
            出错时间 = int(time.time())

            fd, 原始数据存放位置 = tempfile.mkstemp(dir=参数.出错存放文件夹, prefix=f'原始-{出错时间}-', suffix='.wav')
            os.close(fd)
            wavfile.write(原始数据存放位置, 采样率, wav音频数据列表)

            fd, 出错文件 = tempfile.mkstemp(dir=参数.出错存放文件夹, prefix=f'变速-{出错时间}-', suffix='.wav')
            os.close(fd)
            try:
                copy(soundstretch临时输出文件, 出错文件)
            except:
                ...

            fd, soundstretch临时输出文件 = tempfile.mkstemp(dir=参数.出错存放文件夹, prefix=f'变速-{出错时间}-', suffix='.wav')
            os.close(fd)
            变速命令 = f'soundstretch stdin "{soundstretch临时输出文件}" -tempo={(目标速度 - 1) * 100}'
            变速线程 = subprocess.Popen(变速命令, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            变速线程.communicate(内存音频二进制缓存区.getvalue())

            print(f'Soundstretch 音频变速出错了，请前往查看详情\n    原始音频数据：{原始数据存放位置} \n    变速音频数据：{soundstretch临时输出文件}\n')
            print(f'出错的音频信息：\n    音频采样数：{len(wav音频数据列表)}\n    目标速度：{目标速度}\n    目标采样数：{len(wav音频数据列表) / 目标速度}')

            return wav音频数据列表

        os.remove(soundstretch临时输出文件)
    else:
        print(
            '检测到没有安装 SoundTouch 的 soundstretch，所以使用 phasevocoder 的音频变速方法。建议到 http://www.surina.net/soundtouch 下载系统对应的 soundstretch，放到系统环境变量下，可以获得更好的音频变速效果\n')
        sFile = io.BytesIO()
        wavfile.write(sFile, 采样率, wav音频数据列表)
        sFile = io.BytesIO(sFile.getvalue())
        eFile = io.BytesIO()
        with WavReader(sFile) as reader:
            with WavWriter(eFile, reader.channels, reader.samplerate) as writer:
                tsm = phasevocoder(reader.channels, speed=目标速度)
                tsm.run(reader, writer)
        _, 音频区间处理后的数据 = wavfile.read(io.BytesIO(eFile.getvalue()))

    return 音频区间处理后的数据


def 处理音频(音频文件, 片段列表, 视频帧率, 参数: Parameters, concat记录文件路径):
    print(f'\n在子线程开始根据分段信息处理音频')
    速度 = [参数.静音片段速度, 参数.有声片段速度]
    采样率, 总音频数据 = wavfile.read(音频文件, mmap=True)
    最大音量 = 得到最大音量(总音频数据)
    if 最大音量 == 0:
        最大音量 = 1
    衔接前总音频片段末点 = 0  # 上一个帧为空
    concat记录文件 = open(concat记录文件路径, "w", encoding='utf-8')
    输出音频的数据 = np.zeros((0, 总音频数据.shape[1]))  # 返回一个数量为 0 的列表，数据类型为声音 shape[1]
    总片段数量 = len(片段列表)
    每帧采样数 = 采样率 / 视频帧率
    总输出采样数 = 0
    # for index, 片段 in enumerate(片段列表):
    #     print(片段)
    总帧数 = 0
    超出 = 0
    for index, 片段 in enumerate(片段列表):
        # print(f'总共有 {总片段数量} 个音频片段需处理, 现在在处理第 {index + 1} 个：{片段}\n')
        # 音频区间变速处理
        音频区间 = 总音频数据[int(片段[0] * 每帧采样数):int((片段[1]) * 每帧采样数)]
        音频区间处理后的数据 = 音频变速(音频区间, 2, 采样率, 速度[int(片段[2])])
        处理后音频的采样数 = 音频区间处理后的数据.shape[0]
        理论采样数 = int(len(音频区间) / 速度[int(片段[2])])

        # 理想长度 = len(音频区间) / 速度[int(片段[2])]
        # 现实长度 = len(音频区间处理后的数据)
        # 原始帧数 = len(音频区间) / 每帧采样数
        # 理想帧数 = 理想长度 / 每帧采样数
        # 现实帧数 = 现实长度 / 每帧采样数
        # 总帧数 += 现实帧数
        # print(f'这个区间速度为：{速度[int(片段[2])]}\n它的长度为：   {len(音频区间)}\n理想化转换后，长度应为：{理想长度}\n实际长度为：{现实长度}')
        # print(f'这个音频区间速度为：{速度[int(片段[2])]}\n它的长度为：   {原始帧数}\n理想化转换后，长度应为：{理想帧数}\n实际长度为：{现实帧数}\n已写入：{总帧数}')

        if 处理后音频的采样数 < 理论采样数:
            音频区间处理后的数据 = np.concatenate((音频区间处理后的数据, np.zeros((理论采样数 - 处理后音频的采样数, 2), dtype=np.int16)))
        elif 处理后音频的采样数 > 理论采样数:
            音频区间处理后的数据 = 音频区间处理后的数据[0:理论采样数]
            # print(f'片段音频采样数超出：{处理后音频的采样数 - 理论采样数}  此片段速度是：{速度[int(片段[2])]}  它的原长度是：{len(音频区间)}  它的现长度是：{处理后音频的采样数}')
            # 超出 += (处理后音频的采样数 - 理论采样数)
        处理后又补齐的音频的采样数 = 音频区间处理后的数据.shape[0]
        总输出采样数 += 处理后又补齐的音频的采样数

        # self.print('每帧采样数: %s   理论后采样数: %s  处理后采样数: %s  实际转换又补齐后后采样数: %s， 现在总采样数:%s  , 现在总音频时间: %s \n' % (int(self.每帧采样数), 理论采样数, 处理后音频的采样数, 处理后又补齐的音频的采样数, 总输出采样数, 总输出采样数 / (self.视频帧率 * 每帧采样数)  ))
        # 输出音频数据接上 改变后的数据/self.最大音量
        输出音频的数据 = np.concatenate((输出音频的数据, 音频区间处理后的数据 / 最大音量))  # 将刚才处理过后的小片段，添加到输出音频数据尾部
        衔接后总音频片段末点 = 衔接前总音频片段末点 + 处理后音频的采样数

        # 音频区间平滑处理
        if 处理后音频的采样数 < 参数.音频过渡区块大小:
            # 把 0 到 400 的数值都变成0 ，之后乘以音频就会让这小段音频静音。
            输出音频的数据[衔接前总音频片段末点:衔接后总音频片段末点] = 0  # audio is less than 0.01 sec, let's just remove it.
        else:
            # 音频大小渐变蒙板 = np.arange(参数.音频过渡区块大小) / 参数.音频过渡区块大小  # 1 - 400 的等差数列，分别除以 400，得到淡入时每个音频应乘以的系数。
            # 双声道音频大小渐变蒙板 = np.repeat(音频大小渐变蒙板[:, np.newaxis], 2, axis=1)  # 将这个数列乘以 2 ，变成2轴数列，就能用于双声道
            # 输出音频的数据[衔接前总音频片段末点 : 衔接前总音频片段末点 + 参数.音频过渡区块大小] *= 双声道音频大小渐变蒙板  # 淡入
            # 输出音频的数据[衔接后总音频片段末点 - 参数.音频过渡区块大小: 衔接后总音频片段末点] *= 1 - 双声道音频大小渐变蒙板  # 淡出
            pass
        衔接前总音频片段末点 = 衔接后总音频片段末点  # 将这次衔接后的末点作为下次衔接前的末点

        # 根据已衔接长度决定是否将已有总片段写入文件，再新建一个用于衔接的片段
        # print('本音频片段已累计时长：%ss' % str(len(输出音频的数据) / 采样率) )
        # print('输出音频加的帧数: %s' % str(处理后又补齐的音频的采样数 / 每帧采样数) )
        # print(f'\n\nindex: {index}; 总：{总片段数量}\n\n')
        if len(输出音频的数据) >= 采样率 * 60 * 10 or (index + 1) == 总片段数量:
            tempWavClip = tempfile.mkstemp(dir=参数.临时文件夹, prefix='AudioClipForNewVideo_', suffix='.wav')
            os.close(tempWavClip[0])
            wavfile.write(tempWavClip[1], 采样率, 输出音频的数据)
            concat记录文件.write("file " + pathlib.Path(tempWavClip[1]).name + "\n")
            输出音频的数据 = np.zeros((0, 总音频数据.shape[1]))
    # print(f'音频总帧数：{len(输出音频的数据) / 采样率 * 视频帧率}')
    # print(f'总共超出帧数：{超出 / 采样率 * 视频帧率}')
    concat记录文件.close()
    print('子线程中的音频文件处理完毕，只待视频流输出完成了\n')
    return

def pyav处理视频流(参数: Parameters, 临时视频文件, 片段列表):
    片段速度 = [参数.静音片段速度, 参数.有声片段速度]

    # 输入路径 = 'D:/Users/Haujet/Videos/项目/CapsWriter使用/CapsWriter 2.0使用教程.mp4'
    # 输出路径 = 'D:/Users/Haujet/Videos/项目/CapsWriter使用/CapsWriter 2.0使用教程2.mp4'
    input_ = av.open(参数.输入文件)
    inputVideoStream = input_.streams.video[0]
    inputVideoStream.thread_type = 'AUTO'
    width = inputVideoStream.width
    height = inputVideoStream.height
    pix_fmt = inputVideoStream.pix_fmt



    output = av.open(临时视频文件, 'w')
    out_stream = output.add_stream(参数.视频编码器, inputVideoStream.average_rate)
    out_stream.width = width
    out_stream.height = height
    out_stream.pix_fmt  = pix_fmt
    ctx = out_stream.codec_context
    ctx.options = {"crf": f'{参数.视频质量crf参数}'}

    平均帧率 = float(inputVideoStream.average_rate)
    帧率 = float(inputVideoStream.framerate)
    总帧数 = inputVideoStream.frames
    if 总帧数 == 0:
        总帧数 = int(得到输入视频时长(参数.输入文件) * 平均帧率)

    输入等效, 输出等效 = 0, 0
    片段 = 片段列表.pop(0)
    开始时间 = time.time()
    视频帧序号 = 0
    for packet in input_.demux(inputVideoStream):
        for frame in packet.decode():
            视频帧序号 += 1
            if len(片段列表) > 0 and 视频帧序号 >= 片段[1]:
                片段 = 片段列表.pop(0)
            # print(f'视频帧序号：{视频帧序号}   输入等效: {输入等效}   ', end='')
            输入等效 += (1 / 片段速度[片段[2]])
            # print(f'{输入等效}   ')
            if 输入等效 > 输出等效:
                新Frame = av.video.VideoFrame.from_ndarray(frame.to_ndarray(), frame.format.name)
                output.mux(out_stream.encode(新Frame))
                输出等效 += 1
            if 视频帧序号 % 200 == 0:
                print(
                    f'帧速：{int(视频帧序号 / max(time.time() - 开始时间, 1))}, 剩余：{总帧数 - 视频帧序号} 帧，剩余时间：{秒数转时分秒(int((总帧数 - 视频帧序号) / max(1, 视频帧序号 / max(time.time() - 开始时间, 1))))}    \n')
    input_.close()
    output.close()
    print(f'\n视频流处理完毕\n')
    return

def ffmpeg处理视频流(参数: Parameters, 临时视频文件, 片段列表):
    片段速度 = [参数.静音片段速度, 参数.有声片段速度]

    # process1 = (
    #     ffmpeg
    #         .input(参数.输入文件)
    #         .output('pipe:', format='rawvideo', pix_fmt='rgb24')
    #         .run_async(pipe_stdout=True)
    # )
    process1 = subprocess.Popen(['ffmpeg',
                                 '-i', 参数.输入文件,
                                 '-f', 'rawvideo',
                                 '-pix_fmt', 'rgb24',
                                 '-'], stdout=subprocess.PIPE)

    # process1 = subprocess.Popen(f'ffmpeg -i {参数.输入文件} -f rawvideo', stdout=subprocess.PIPE)

    输入视频容器 = av.open(参数.输入文件)
    输入视频容器.streams.video[0].thread_type = 'AUTO'
    视频流 = 输入视频容器.streams.video[0]
    平均帧率 = float(视频流.average_rate)
    帧率 = float(视频流.framerate)
    总帧数 = 视频流.frames
    if 总帧数 == 0:
        总帧数 = int(得到输入视频时长(参数.输入文件) * 平均帧率)
    格式 = format
    像素格式 = 视频流.pix_fmt
    宽度 = 视频流.width
    高度 = 视频流.height
    输入视频容器.close()
    # process2 = (
    #     ffmpeg
    #         .input('pipe:', format='rawvideo', pix_fmt='rgb24', s='{}x{}'.format(宽度, 高度), framerate=平均帧率)
    #         .output(临时视频文件, pix_fmt=像素格式, vcodec=参数.视频编码器, crf=参数.视频质量crf参数)
    #         .overwrite_output()
    #         .run_async(pipe_stdin=True)
    # )
    process2 = subprocess.Popen(['ffmpeg', '-y',
                                 '-f', 'rawvideo',
                                 '-vcodec', 'rawvideo',
                                 '-pix_fmt', 'rgb24',
                                 '-s', f'{宽度}*{高度}',
                                 '-framerate', f'{平均帧率}',
                                 '-i', '-',
                                 '-pix_fmt', 像素格式,
                                 '-vcodec', 参数.视频编码器,
                                 '-crf', f'{参数.视频质量crf参数}',
                                 临时视频文件], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    开始时间 = time.time()
    片段 = 片段列表.pop(0)
    输入等效, 输出等效 = 0, 0
    index = 0
    while True:
        index += 1
        in_bytes = process1.stdout.read(宽度 * 高度 * 3)
        if not in_bytes:
            break
        if len(片段列表) > 0 and index >= 片段[1]:
            片段 = 片段列表.pop(0)
        输入等效 += (1 / 片段速度[片段[2]])
        # print(f'输入等效: {输入等效}    输出等效:{输出等效}')
        while 输入等效 > 输出等效:
            # in_frame = (
            #     np
            #         .frombuffer(in_bytes, np.uint8)
            #         .reshape([宽度, 高度, 3])
            # )
            # process2.stdin.write(
            #     in_frame
            #         .astype(np.uint8)
            #         .tobytes()
            # )
            process2.stdin.write(
                in_bytes
            )
            # process2.stdin.flush()
            # process2.communicate(
            #     in_bytes
            # )
            输出等效 += 1
        if index % 200 == 0:
            print(
                f'帧速：{int(index / max(time.time() - 开始时间, 1))}, 剩余：{总帧数 - index} 帧，剩余时间：{秒数转时分秒(int((总帧数 - index) / max(1, index / max(time.time() - 开始时间, 1))))}    \n')
    process2.stdin.close()
    process1.wait()
    process2.wait()
    print(f'\n原来视频长度：{总帧数 / 平均帧率 / 60} 分钟，输出视频长度：{int(输出等效) / 平均帧率 / 60} 分钟\n')

def 计算总共帧数(片段列表, 片段速度):
    总共帧数 = 0.0
    for 片段 in 片段列表:
        总共帧数 += (片段[1] - 片段[0]) / 片段速度[片段[2]]
    return int(总共帧数)

# @profile()
def ffmpeg和pyav综合处理视频流(参数: Parameters, 临时视频文件, 片段列表):
    开始时间 = time.time()
    片段速度 = [参数.静音片段速度, 参数.有声片段速度]

    input_ = av.open(参数.输入文件)
    inputVideoStream = input_.streams.video[0]
    inputVideoStream.thread_type = 'AUTO'
    平均帧率 = float(inputVideoStream.average_rate)

    输入视频流查询命令 = f'ffprobe -of json -select_streams v -show_streams "{参数.输入文件}"'
    输入视频流查询结果 = subprocess.run(输入视频流查询命令, capture_output=True, encoding='utf-8')
    输入视频流信息 = json.loads(输入视频流查询结果.stdout)
    del 输入视频流查询结果
    color_primaries = 输入视频流信息['streams'][0]['color_primaries']
    color_range = 输入视频流信息['streams'][0]['color_range']
    color_space = 输入视频流信息['streams'][0]['color_space']
    color_transfer = 输入视频流信息['streams'][0]['color_transfer']
    field_order = 输入视频流信息['streams'][0]['field_order']
    height = 输入视频流信息['streams'][0]['coded_height']
    width = 输入视频流信息['streams'][0]['coded_width']
    pix_fmt = 输入视频流信息['streams'][0]['pix_fmt']
    # 用 ffprobe 获得信息：
    # ffprobe -of json -select_streams v -show_entries stream=r_frame_rate "D:\Users\Haujet\Videos\2020-11-04 18-16-56.mkv"
    process2Command = ['ffmpeg', '-y',
                                 '-f', 'rawvideo',
                                 '-vcodec', 'rawvideo',
                                 '-pix_fmt', pix_fmt,
                                 '-color_primaries', f'{color_primaries}',
                                 '-color_range', f'{color_range}',
                                 '-colorspace', f'{color_space}',
                                 '-field_order', f'{field_order}',
                                 '-color_trc', f'{color_transfer}',
                                 '-s', f'{width}*{height}',
                                 '-frame_size', f'{width}*{height}',
                                 '-framerate', f'{平均帧率}',
                                 '-i', '-',
                                 '-s', f'{width}*{height}',
                                 '-vcodec', 参数.视频编码器,
                                 '-crf', f'{参数.视频质量crf参数}',
                                 临时视频文件]
    print(process2Command)
    process2 = subprocess.Popen(process2Command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    帧率 = float(inputVideoStream.framerate)
    原始总帧数 = inputVideoStream.frames
    if 原始总帧数 == 0:
        原始总帧数 = int(得到输入视频时长(参数.输入文件) * 平均帧率)
    总帧数 = 计算总共帧数(片段列表, 片段速度)

    print(f'\n输出视频总帧数：{int(总帧数)}，输出后时长：{秒数转时分秒(int(总帧数 / 平均帧率))}\n')

    输入等效, 输出等效 = 0.0, 0.0
    片段 = 片段列表.pop(0)
    开始时间 = time.time()
    视频帧序号 = 0
    index = 0
    for packet in input_.demux(inputVideoStream):
        for frame in packet.decode():
            frame = frame.reformat()
            index += 1
            if len(片段列表) > 0 and index >= 片段[1]:片段 = 片段列表.pop(0)
            输入等效 += (1 / 片段速度[片段[2]])
            while 输入等效 > 输出等效:
                # 经过测试得知，在一些分辨率的视频中，例如一行虽然只有 2160 个像素，但是这一行的数据不止 2160 个，有可能是2176个，然后所有行的数据是连在一起的
                # 在 python 里很难分离，只能使用 pyav 的 to_ndarray 再 tobytes
                if frame.planes[1].width != frame.planes[0].line_size:
                    # in_bytes = frame.to_ndarray().astype(np.uint8).tobytes()
                    in_bytes = frame.to_ndarray().tobytes()
                    process2.stdin.write(in_bytes)
                else:
                    if frame.format.name in ('yuv420p', 'yuvj420p'):
                        process2.stdin.write(frame.planes[0].to_bytes())
                        process2.stdin.write(frame.planes[1].to_bytes())
                        process2.stdin.write(frame.planes[2].to_bytes())
                    elif frame.format.name in ('yuyv422', 'rgb24', 'bgr24', 'argb', 'rgba', 'abgr', 'bgra', 'gray', 'gray8', 'rgb8', 'bgr8', 'pal8'):
                        process2.stdin.write(frame.planes[0].to_bytes())
                    else:
                        print(f'{frame.format.name} 像素格式不支持')
                        return False

                输出等效 += 1
                if 输出等效 % 200 == 0:
                    print(
                        f'帧速：{int(int(输出等效) / max(time.time() - 开始时间, 1))}, 剩余：{总帧数 - int(输出等效)} 帧，剩余时间：{秒数转时分秒(int((总帧数 - int(输出等效)) / max(1, int(输出等效) / max(time.time() - 开始时间, 1))))}    \n')
    process2.stdin.close()
    process2.wait()
    del process2
    print(f'\n输出视频总帧数：{int(总帧数)}，输出后时长：{秒数转时分秒(int(总帧数 / 平均帧率))}')
    print(f'\n原来视频长度：{原始总帧数 / 平均帧率 / 60} 分钟，输出视频长度：{int(输出等效) / 平均帧率 / 60} 分钟\n')
    print(f'\n视频合成耗时：{秒数转时分秒(time.time() - 开始时间)}\n')
    return 

def 秒数转时分秒(秒数):
    秒数 = int(秒数)
    输出 = ''
    if 秒数 // 3600 > 0:
        输出 = f'{输出}{秒数 // 3600} 小时 '
        秒数 = 秒数 % 3600
    if 秒数 // 60 > 0:
        输出 = f'{输出}{秒数 // 60} 分 '
        秒数 = 秒数 % 60
    输出 = f'{输出}{秒数} 秒'
    return 输出

# @profile()
def main():
    开始时间 = time.time()

    参数 = Parameters()
    参数.得到参数()

    # 得到视频帧率
    if 参数.只处理音频:
        视频帧率 = 30
    else:
        视频帧率 = 得到输入视频帧率(参数.输入文件)
        视频时长 = 得到输入视频时长(参数.输入文件)
        if 视频帧率 == None: # 如果得不到视频帧率，说明没有视频轨，只处理音频
            print(f'无法得到视频帧率，认为输入只包含音频')
            参数.只处理音频 = True
            视频帧率 = 30

    # 得到音频采样率
    if 参数.辅助音频文件 != '':
        采样率 = 得到输入音频采样率(参数.辅助音频文件)
    else:
        采样率 = 得到输入音频采样率(参数.输入文件)

    # 设定音频路径
    if 参数.使用spleeter生成辅助音频 or 参数.辅助音频文件 != '':
        分析用的音频文件 = (pathlib.Path(参数.临时文件夹) / 'AnalyticAudio.wav').as_posix()
        变速用的音频文件 = (pathlib.Path(参数.临时文件夹) / 'OriginalAudio.wav').as_posix()
    else:
        分析用的音频文件 = (pathlib.Path(参数.临时文件夹) / 'OriginalAudio.wav').as_posix()
        变速用的音频文件 = (pathlib.Path(参数.临时文件夹) / 'OriginalAudio.wav').as_posix()

    # 提取原始音频
    提取音频流(参数.输入文件, 变速用的音频文件, 采样率)

    # 得到辅助音频
    if 参数.使用spleeter生成辅助音频:
        由spleeter得到分析音频(输入文件=变速用的音频文件, 输出文件=分析用的音频文件, 参数=参数)
    elif 参数.辅助音频文件 != '':
        提取音频流(参数.辅助音频文件, 分析用的音频文件, 采样率)
    else:
        ...

    # 从音频得到片段列表
    片段列表 = 由音频得到片段列表(音频文件=分析用的音频文件, 视频帧率=视频帧率, 参数=参数)
    # 打印列表(片段列表)



    concat记录文件 = (pathlib.Path(参数.临时文件夹) / 'concat.txt').as_posix()
    音频处理线程 = threading.Thread(target=处理音频, args=[变速用的音频文件, 片段列表.copy(), 视频帧率, 参数, concat记录文件])
    音频处理线程.start()

    if not 参数.只处理音频:
        临时视频文件 = (pathlib.Path(参数.临时文件夹) / 'Video.mp4').as_posix()
        # pyav处理视频流(参数, 临时视频文件, 片段列表)
        # ffmpeg处理视频流(参数, 临时视频文件, 片段列表)
        ffmpeg和pyav综合处理视频流(参数, 临时视频文件, 片段列表)

    音频处理线程.join()

    print(f'现在开始合并')  # 合并音视频
    if 参数.只处理音频:
        command = f'ffmpeg -y -hide_banner -safe 0  -f concat -i "{concat记录文件}" -i "{参数.输入文件}" -c:v copy -map_metadata 1 -map_metadata:s:a 1:s:a -map 0:a "{参数.输出文件}"'
    else:
        command = f'ffmpeg -y -hide_banner -i "{临时视频文件}" -safe 0 -f concat -i "{concat记录文件}" -i "{参数.输入文件}" -c:v copy -map_metadata 2 -map_metadata:s:a 2:s:a -map_metadata:s:v 2:s:v -map 0:v -map 1:a  "{参数.输出文件}"'
    subprocess.run(command, encoding='utf-8', stderr=subprocess.PIPE)
    try:
        rmtree(参数.临时文件夹)
        ...
    except Exception as e:
        print(f'删除临时文件夹失败，可能是被占用导致，请手动删除：\n    {参数.临时文件夹}')
    if platform.system() == 'Windows':
        os.system(f'explorer /select, "{pathlib.Path(参数.输出文件)}')
    else:
        os.startfile(pathlib.Path(参数.输出文件).parent)
    print(f'\n总共耗时：{秒数转时分秒(time.time() - 开始时间)}\n')
    input('\n处理完毕，回车关闭\n')
    return 


if __name__ == '__main__':
    main()




