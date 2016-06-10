python.exe setup2.py py2exe
xcopy images dist\images\ /Y /E
xcopy locale dist\locale\ /Y /E
xcopy Slic3r dist\Slic3r\ /Y /E
copy MSVCP90.DLL dist\
pause
