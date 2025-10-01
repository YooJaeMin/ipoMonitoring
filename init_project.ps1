# Azure Functions 프로젝트 초기화 스크립트
# UTF-8 인코딩 설정
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "Azure Functions 프로젝트 초기화 시작" -ForegroundColor Green

# 1. Azure Functions Core Tools 설치 확인
Write-Host "Azure Functions Core Tools 설치 확인..." -ForegroundColor Cyan
try {
    func --version | Out-Null
    if ($LASTEXITCODE -ne 0) { throw }
    Write-Host "Azure Functions Core Tools가 이미 설치되어 있습니다." -ForegroundColor Green
} catch {
    Write-Host "Azure Functions Core Tools가 설치되지 않았습니다." -ForegroundColor Red
    Write-Host "다음 명령어로 설치하세요:" -ForegroundColor Yellow
    Write-Host "npm install -g azure-functions-core-tools@4 --unsafe-perm true" -ForegroundColor Yellow
    Read-Host "설치 후 Enter를 누르세요"
}

# 2. Python 가상환경 생성
Write-Host "Python 가상환경 생성..." -ForegroundColor Cyan
if (Test-Path ".venv") {
    Write-Host "가상환경이 이미 존재합니다." -ForegroundColor Yellow
} else {
    python -m venv .venv
    Write-Host "가상환경이 생성되었습니다." -ForegroundColor Green
}

# 3. 가상환경 활성화
Write-Host "가상환경 활성화..." -ForegroundColor Cyan
.venv\Scripts\Activate.ps1

# 4. 의존성 설치
Write-Host "Python 패키지 설치..." -ForegroundColor Cyan
pip install -r requirements.txt

# 5. 로컬 테스트
Write-Host "로컬 테스트 실행..." -ForegroundColor Cyan
Write-Host "로컬에서 함수를 테스트합니다. Ctrl+C로 종료하세요." -ForegroundColor Yellow
func start

Write-Host "프로젝트 초기화 완료!" -ForegroundColor Green
Write-Host "이제 Azure에 배포할 수 있습니다." -ForegroundColor Cyan