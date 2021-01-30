set ����=JumpCutter-Improved

set ��������=launcher

set ������·��=..\launcher\%��������%.py

set �ų��б�=exclude.txt

:: �� packages��pretrained_models �Ӵ��Ŀ¼�ƶ������õط�
move .\dist\%��������%\site-packages .\dist\site-packages
move .\dist\%��������%\pretrained_models .\dist\pretrained_models
move .\dist\%��������%\bin .\dist\bin

:: �������ͽ���
if "%errorlevel%"=="1" goto :end


:: ���������
..\Scripts\pyinstaller --noconfirm ^
					--hidden-import json ^
					--hidden-import wave ^
					--hidden-import site ^
					--hidden-import fractions ^
					--hidden-import timeit ^
					--hidden-import xml.dom ^
					--hidden-import uuid ^
					--hidden-import distutils.version ^
					--hidden-import imp ^
					--hidden-import unittest.mock ^
					--hidden-import cProfile ^
					--hidden-import http.cookies ^
					--hidden-import importlib.resources ^
					"%������·��%"

:: ���� spleeter ģ��
::echo d | xcopy /s /y ..\src\pretrained_models .\dist\%��������%\pretrained_models

:: �����ų��б�
echo \pretrained_models\ > %�ų��б�%
echo \test\ >> %�ų��б�%
echo \bin\ >> %�ų��б�%
echo \__pycache__\ >> %�ų��б�%

:: �� packages��pretrained_models �ƶ������Ŀ¼
move .\dist\site-packages .\dist\%��������%\site-packages 
move .\dist\pretrained_models .\dist\%��������%\pretrained_models 
move .\dist\bin .\dist\%��������%\bin 

:: exe ������
del .\dist\%��������%\_%����%.exe
ren .\dist\%��������%\%��������%.exe  "___%����%.exe"

:: 7z ѹ�������ļ�
del /F /Q �����ļ�-%����%.7z
7z a -t7z �����ļ�-%����%.7z .\dist\%��������%\* -mx=9 -ms=200m -mf -mhc -mhcf  -mmt -r

:: ���� py Դ�ļ������� src �ļ���
rmdir /s /q .\dist\src
echo d | xcopy /s /y /EXCLUDE:%�ų��б�% ..\src .\dist\src

:: 7z ѹ��Դ����
del /F /Q Դ����-%����%.7z
7z a -t7z Դ����-%����%.7z .\dist\src\* -mx=9 -ms=200m -mf -mhc -mhcf  -mmt -r

:: ��Դ�����ƶ��� launcher �ļ���
move .\dist\src\* .\dist\%��������%

:: ���в���
cd ".\dist\%��������%"
"___%����%.exe"

:end
pause