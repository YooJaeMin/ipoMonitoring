@echo off
chcp 65001
powershell -Command "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; .\check_deployment.ps1"
pause
