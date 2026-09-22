@echo off
chcp 65001 >nul
title 一键抹除视频海外元数据与平台抬头 (防国内平台查重与违规)
cls

echo ======================================================================
echo    VidSnap 视频元数据清洗与平台抬头抹除工具
echo    作用：彻底清除 YouTube / X / Google 等海外平台特征签名与防盗标记
echo    效果：伪装为原生剪辑/相机拍摄文件，无损、不重编码、1秒完成
echo ======================================================================
echo.

if "%~1"=="" goto :BATCH_MODE

:DRAG_MODE
echo 正在处理拖入的文件: %~nx1
ffmpeg -hide_banner -y -i "%~1" -map_metadata -1 -metadata:s:v:0 handler_name="VideoHandler" -metadata:s:a:0 handler_name="SoundHandler" -c copy "%~dpn1_clean%~x1"
if %ERRORLEVEL% EQU 0 (
    echo.
    echo [成功] 已生成纯净视频: "%~dpn1_clean%~x1"
    echo 已抹除所有 Google/YouTube/X 特征抬头与内置元数据！
) else (
    echo.
    echo [错误] 处理失败，请检查文件格式。
)
shift
if not "%~1"=="" goto :DRAG_MODE
echo.
echo 全部处理完成！按任意键退出...
pause >nul
exit /b

:BATCH_MODE
echo 没有拖入单个文件，将自动扫描并清洗 downloads 目录下的所有视频...
echo.

set TARGET_DIR=%~dp0downloads
if not exist "%TARGET_DIR%" (
    echo 未找到 downloads 文件夹。
    echo 提示：你可以直接把想要清洗的视频文件【拖动到这个 bat 图标上】即可清洗！
    pause
    exit /b
)

for %%f in ("%TARGET_DIR%\*.mp4" "%TARGET_DIR%\*.m4a" "%TARGET_DIR%\*.mkv") do (
    echo 正在净化: %%~nxf
    ffmpeg -hide_banner -y -i "%%f" -map_metadata -1 -metadata:s:v:0 handler_name="VideoHandler" -metadata:s:a:0 handler_name="SoundHandler" -c copy "%%~dpnf_temp%%~xf" >nul 2>&1
    if exist "%%~dpnf_temp%%~xf" (
        move /y "%%~dpnf_temp%%~xf" "%%f" >nul
        echo    - [完成] 已抹除平台抬头与特征
    )
)

echo.
echo ======================================================================
echo 🎉 downloads 目录下的所有视频已全部清洗完毕！
echo 已重置为无平台特征状态，可放心在国内平台发布。
echo ======================================================================
pause
