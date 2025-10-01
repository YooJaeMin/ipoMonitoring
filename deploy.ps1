# Azure Function App 배포 스크립트 (PowerShell)
# 사용법: .\deploy.ps1 [function-app-name] [resource-group-name]

param(
    [string]$FunctionAppName = "myFRMINotifier",
    [string]$ResourceGroup = "myResourceGroup"
)

$Location = "koreacentral"
$StorageAccount = "$FunctionAppName" + "storage" + (Get-Date -Format "yyyyMMddHHmmss").Substring(8,4)

Write-Host "🚀 Azure Function App 배포 시작" -ForegroundColor Green
Write-Host "Function App Name: $FunctionAppName" -ForegroundColor Yellow
Write-Host "Resource Group: $ResourceGroup" -ForegroundColor Yellow
Write-Host "Location: $Location" -ForegroundColor Yellow
Write-Host "Storage Account: $StorageAccount" -ForegroundColor Yellow

# Azure CLI 설치 확인
try {
    az --version | Out-Null
    if ($LASTEXITCODE -ne 0) { throw }
} catch {
    Write-Host "❌ Azure CLI가 설치되지 않았습니다. https://aka.ms/installazurecliwindows 에서 설치하세요." -ForegroundColor Red
    Read-Host "계속하려면 Enter를 누르세요"
    exit 1
}

# Azure 로그인 확인
Write-Host "🔐 Azure 로그인 상태 확인..." -ForegroundColor Cyan
try {
    az account show | Out-Null
    if ($LASTEXITCODE -ne 0) { throw }
} catch {
    Write-Host "Azure에 로그인해주세요..." -ForegroundColor Yellow
    az login
}

# 리소스 그룹 생성
Write-Host "📁 리소스 그룹 생성 중..." -ForegroundColor Cyan
az group create --name $ResourceGroup --location $Location

# Storage Account 생성
Write-Host "💾 Storage Account 생성 중..." -ForegroundColor Cyan
az storage account create --name $StorageAccount --location $Location --resource-group $ResourceGroup --sku Standard_LRS

# Function App 생성
Write-Host "⚡ Function App 생성 중..." -ForegroundColor Cyan
az functionapp create --resource-group $ResourceGroup --consumption-plan-location $Location --runtime python --runtime-version 3.9 --functions-version 4 --name $FunctionAppName --storage-account $StorageAccount

# 환경 변수 설정
Write-Host "⚙️ 환경 변수 설정 중..." -ForegroundColor Cyan
Write-Host "다음 정보를 입력해주세요:" -ForegroundColor Yellow

$EmailSender = Read-Host "발신 이메일 주소"
$EmailReceiver = Read-Host "수신 이메일 주소"
$EmailPassword = Read-Host "이메일 비밀번호/앱 비밀번호" -AsSecureString
$EmailPasswordText = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($EmailPassword))
$SmtpServer = Read-Host "SMTP 서버 [기본값: smtp.gmail.com]"
if ([string]::IsNullOrEmpty($SmtpServer)) { $SmtpServer = "smtp.gmail.com" }
$SmtpPort = Read-Host "SMTP 포트 [기본값: 587]"
if ([string]::IsNullOrEmpty($SmtpPort)) { $SmtpPort = "587" }

az functionapp config appsettings set --name $FunctionAppName --resource-group $ResourceGroup --settings EMAIL_SENDER="$EmailSender" EMAIL_RECEIVER="$EmailReceiver" EMAIL_PASSWORD="$EmailPasswordText" SMTP_SERVER="$SmtpServer" SMTP_PORT="$SmtpPort"

# Azure Functions Core Tools 설치 확인
try {
    func --version | Out-Null
    if ($LASTEXITCODE -ne 0) { throw }
} catch {
    Write-Host "❌ Azure Functions Core Tools가 설치되지 않았습니다." -ForegroundColor Red
    Write-Host "다음 명령어로 설치하세요:" -ForegroundColor Yellow
    Write-Host "npm install -g azure-functions-core-tools@4 --unsafe-perm true" -ForegroundColor Yellow
    Read-Host "계속하려면 Enter를 누르세요"
    exit 1
}

# 배포 실행
Write-Host "📦 Function App 배포 중..." -ForegroundColor Cyan
func azure functionapp publish $FunctionAppName --python

Write-Host "✅ 배포 완료!" -ForegroundColor Green
Write-Host ""
Write-Host "🔗 Function App URL: https://$FunctionAppName.azurewebsites.net" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 로그 확인:" -ForegroundColor Yellow
Write-Host "az functionapp logs tail --name $FunctionAppName --resource-group $ResourceGroup" -ForegroundColor Gray

Read-Host "계속하려면 Enter를 누르세요"
