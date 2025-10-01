@echo off
chcp 65001
powershell -Command "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; .\init_project.ps1"
pause
