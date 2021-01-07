set 名字=JumpCutter-Improved

del /F /Q %名字%.7z

7z a -t7z %名字%.7z Lib Scripts src 运行.bat LICENSE README.md -mx=9 -ms=200m -mf -mhc -mhcf  -mmt -r

pause