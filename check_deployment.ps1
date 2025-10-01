# Azure Functions 배포 전 체크리스트
# UTF-8 인코딩 설정
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "Azure Functions 배포 전 체크리스트" -ForegroundColor Green
Write-Host "=" * 50

$errors = @()

# 1. 필수 파일 확인
Write-Host "필수 파일 확인..." -ForegroundColor Cyan

$requiredFiles = @("init.py", "function.json", "host.json", "requirements.txt")
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "OK: $file" -ForegroundColor Green
    } else {
        Write-Host "ERROR: $file (누락)" -ForegroundColor Red
        $errors += $file
    }
}

# 2. function.json 내용 확인
Write-Host "`nfunction.json 내용 확인..." -ForegroundColor Cyan
try {
    $functionJson = Get-Content "function.json" | ConvertFrom-Json
    if ($functionJson.scriptFile -eq "init.py") {
        Write-Host "OK: scriptFile: init.py" -ForegroundColor Green
    } else {
        Write-Host "ERROR: scriptFile이 잘못됨: $($functionJson.scriptFile)" -ForegroundColor Red
        $errors += "function.json scriptFile"
    }
    
    if ($functionJson.bindings[0].type -eq "timerTrigger") {
        Write-Host "OK: timerTrigger 설정됨" -ForegroundColor Green
    } else {
        Write-Host "ERROR: timerTrigger 설정이 잘못됨" -ForegroundColor Red
        $errors += "function.json timerTrigger"
    }
} catch {
    Write-Host "ERROR: function.json 파싱 오류" -ForegroundColor Red
    $errors += "function.json parse error"
}

# 3. Python 파일 문법 확인
Write-Host "`nPython 파일 문법 확인..." -ForegroundColor Cyan
try {
    python -m py_compile init.py
    Write-Host "OK: init.py 문법 오류 없음" -ForegroundColor Green
} catch {
    Write-Host "ERROR: init.py 문법 오류" -ForegroundColor Red
    $errors += "init.py syntax error"
}

# 4. Azure CLI 로그인 확인
Write-Host "`nAzure CLI 로그인 확인..." -ForegroundColor Cyan
try {
    $account = az account show 2>$null | ConvertFrom-Json
    if ($account) {
        Write-Host "OK: Azure에 로그인됨: $($account.user.name)" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Azure에 로그인되지 않음" -ForegroundColor Red
        $errors += "Azure login"
    }
} catch {
    Write-Host "ERROR: Azure CLI 오류" -ForegroundColor Red
    $errors += "Azure CLI"
}

# 5. Azure Functions Core Tools 확인
Write-Host "`nAzure Functions Core Tools 확인..." -ForegroundColor Cyan
try {
    $funcVersion = func --version 2>$null
    if ($funcVersion) {
        Write-Host "OK: Azure Functions Core Tools: $funcVersion" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Azure Functions Core Tools 없음" -ForegroundColor Red
        $errors += "Azure Functions Core Tools"
    }
} catch {
    Write-Host "ERROR: Azure Functions Core Tools 오류" -ForegroundColor Red
    $errors += "Azure Functions Core Tools"
}

# 결과 출력
Write-Host "`n" + "=" * 50
if ($errors.Count -eq 0) {
    Write-Host "모든 체크 통과! 배포 준비 완료!" -ForegroundColor Green
    Write-Host "다음 명령어로 배포하세요:" -ForegroundColor Cyan
    Write-Host "func azure functionapp publish [함수앱이름]" -ForegroundColor Yellow
} else {
    Write-Host "다음 문제들을 해결하세요:" -ForegroundColor Red
    foreach ($error in $errors) {
        Write-Host "  - $error" -ForegroundColor Red
    }
}