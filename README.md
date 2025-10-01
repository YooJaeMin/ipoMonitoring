# FRMI 주식 상장 알림 서비스 (스마트 모니터링)

Azure Function App을 사용하여 FRMI 주식의 상장 여부를 스마트하게 모니터링하고, 상장이 확인되면 이메일로 알림을 발송하는 서비스입니다.

## 🚀 주요 기능

1. **스마트 모니터링**: 매일 KST 오후 9시 30분부터 다음날 오전 6시까지만 모니터링
2. **지능적 알림**: 
   - 상장되지 않았을 때: 1시간마다 상태 알림
   - 상장 확인 시: 즉시 알림 + 모니터링 자동 종료
3. **Yahoo Finance 연동**: yfinance 라이브러리를 통한 실시간 주식 데이터 확인
4. **이메일 알림**: SMTP를 통한 HTML 형식의 상장 알림 발송
5. **Azure App Settings**: 보안을 위한 환경 변수 기반 설정

## ⏰ 모니터링 스케줄

- **모니터링 시간**: 매일 21:30 ~ 다음날 06:00 (KST)
- **알림 주기**: 
  - 상장되지 않았을 때: 1시간마다 상태 알림
  - 상장 확인 시: 즉시 알림 + 모니터링 종료
- **모니터링 시간 외**: 알림 발송하지 않음

## 📧 이메일 알림 종류

### 1. 상장 확인 알림 (즉시 발송)
- 상장이 확인되면 즉시 발송
- 모니터링 자동 종료 안내
- 상장 정보 상세 표시

### 2. 모니터링 상태 알림 (1시간마다)
- 아직 상장되지 않았을 때 발송
- 모니터링 진행 상황 안내
- 다음 알림 시간 안내

## 설치 및 설정

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`local.settings.json` 파일에서 다음 값들을 설정하세요:

```json
{
  "EMAIL_SENDER": "your-email@gmail.com",
  "EMAIL_RECEIVER": "recipient-email@gmail.com", 
  "EMAIL_PASSWORD": "your-app-password",
  "SMTP_SERVER": "smtp.gmail.com",
  "SMTP_PORT": "587"
}
```

### 3. Gmail 앱 비밀번호 설정

Gmail을 사용하는 경우 앱 비밀번호를 생성해야 합니다:

1. Google 계정 설정 → 보안
2. 2단계 인증 활성화
3. 앱 비밀번호 생성
4. 생성된 비밀번호를 `EMAIL_PASSWORD`에 설정

### 4. 로컬 실행

```bash
# 즉시 테스트 (한 번만 실행)
python test_local.py

# 지속적 모니터링 (스케줄러 사용)
python scheduler_test.py
```

## Azure 배포

### Azure CLI를 사용한 배포

```bash
# Azure에 로그인
az login

# 리소스 그룹 생성
az group create --name myResourceGroup --location koreacentral

# Storage Account 생성
az storage account create --name mystorageaccount --location koreacentral --resource-group myResourceGroup --sku Standard_LRS

# Function App 생성
az functionapp create --resource-group myResourceGroup --consumption-plan-location koreacentral --runtime python --runtime-version 3.9 --functions-version 4 --name myFRMINotifier --storage-account mystorageaccount

# 환경 변수 설정
az functionapp config appsettings set --name myFRMINotifier --resource-group myResourceGroup --settings EMAIL_SENDER="your-email@gmail.com" EMAIL_RECEIVER="recipient-email@gmail.com" EMAIL_PASSWORD="your-app-password" SMTP_SERVER="smtp.gmail.com" SMTP_PORT="587"

# 배포
func azure functionapp publish myFRMINotifier
```

## App Settings 설정

Azure Portal에서 다음 App Settings를 설정하세요:

| 설정 이름 | 값 | 설명 |
|-----------|-----|------|
| `EMAIL_SENDER` | `yoose92@gmail.com` | 발신 이메일 주소 |
| `EMAIL_RECEIVER` | `yoose92@gmail.com` | 수신 이메일 주소 |
| `EMAIL_PASSWORD` | `cxifsbzswvwavchs` | 이메일 비밀번호/앱 비밀번호 |
| `SMTP_SERVER` | `smtp.gmail.com` | SMTP 서버 주소 |
| `SMTP_PORT` | `587` | SMTP 포트 |

## 모니터링 동작 방식

1. **타이머 트리거**: 5분마다 자동 실행
2. **시간 확인**: 현재 시간이 모니터링 시간인지 확인 (21:30 ~ 06:00 KST)
3. **주식 데이터 확인**: Yahoo Finance API를 통해 FRMI 주식 데이터 조회
4. **상장 여부 판단**: 
   - 데이터가 존재하면 상장된 것으로 판단 → 즉시 알림 + 모니터링 종료
   - 데이터가 없으면 아직 상장되지 않음 → 1시간마다 상태 알림
5. **로깅**: 모든 과정을 Azure Functions 로그에 기록

## 로컬 테스트 방법

### 1. 즉시 테스트
```bash
python test_local.py
```

### 2. 지속적 모니터링 테스트
```bash
# schedule 패키지 설치
pip install schedule

# 스케줄러 실행
python scheduler_test.py
```

### 3. 모니터링 시간 확인
- 현재 시간이 21:30 ~ 06:00 (KST) 사이인지 확인
- 모니터링 시간 외에는 알림을 발송하지 않음

## 주의사항

- **시간대**: 모든 시간은 KST(한국 표준시) 기준입니다
- **Gmail 앱 비밀번호**: Gmail 사용 시 일반 비밀번호가 아닌 앱 비밀번호 사용
- **모니터링 종료**: 상장이 확인되면 자동으로 모니터링이 종료됩니다
- **Azure Function의 실행 시간 제한**: 최대 5분을 고려해야 합니다

## 문제 해결

### 이메일 발송 실패 시
1. EMAIL_SENDER, EMAIL_RECEIVER, EMAIL_PASSWORD 설정 확인
2. Gmail 앱 비밀번호 사용 여부 확인
3. SMTP 서버 및 포트 설정 확인

### 주식 데이터 조회 실패 시
1. 인터넷 연결 상태 확인
2. Yahoo Finance API 상태 확인
3. FRMI 종목 코드 정확성 확인

### 모니터링 시간 확인
- 현재 시간이 21:30 ~ 06:00 (KST) 사이인지 확인
- pytz 패키지가 설치되어 있는지 확인