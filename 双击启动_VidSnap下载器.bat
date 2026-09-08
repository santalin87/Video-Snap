@echo off
chcp 65001 >nul
title VidSnap 本地极速下载器
cls

echo =======================================================
echo          VidSnap 本地极速下载器
echo    (使用本地网络跑满带宽，不消耗任何 VPS 流量)
echo =======================================================
echo.

python "%~dp0vidsnap_local.py"

pause
