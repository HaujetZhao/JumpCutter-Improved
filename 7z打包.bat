set ����=JumpCutter-Improved

del /F /Q %����%.7z

7z a -t7z %����%.7z Lib Scripts src ����.bat LICENSE README.md -mx=9 -ms=200m -mf -mhc -mhcf  -mmt -r

pause