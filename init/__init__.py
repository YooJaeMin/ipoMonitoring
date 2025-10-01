import datetime
import logging
import requests
import smtplib
import os
import json
import time
import threading
from email.mime.text import MIMEText
import pytz

import azure.functions as func

TICKER = "FRMI"

# 전역 상태 관리 변수
MONITORING_ACTIVE = True
LAST_NOTIFICATION_TIME = None
LISTING_CONFIRMED = False

def get_kst_time():
    """한국 시간(KST)을 반환합니다."""
    kst = pytz.timezone('Asia/Seoul')
    return datetime.datetime.now(kst)

def is_monitoring_time():
    """현재 시간이 모니터링 시간인지 확인합니다."""
    kst_time = get_kst_time()
    current_hour = kst_time.hour
    current_minute = kst_time.minute
    
    # 오후 9시 30분부터 다음날 오전 6시까지
    if current_hour >= 21 and current_minute >= 30:
        return True
    elif current_hour < 6:
        return True
    else:
        return False

def should_send_notification():
    """1시간마다 알림을 보낼지 결정합니다."""
    global LAST_NOTIFICATION_TIME
    
    if LAST_NOTIFICATION_TIME is None:
        return True
    
    kst_time = get_kst_time()
    time_diff = kst_time - LAST_NOTIFICATION_TIME
    
    # 1시간(3600초) 이상 경과했으면 알림 발송
    return time_diff.total_seconds() >= 3600

def update_last_notification_time():
    """마지막 알림 시간을 업데이트합니다."""
    global LAST_NOTIFICATION_TIME
    LAST_NOTIFICATION_TIME = get_kst_time()

def send_email_alert(message: str, subject_suffix: str = ""):
    """이메일 알림을 발송합니다."""
    sender = os.getenv('EMAIL_SENDER')
    receiver = os.getenv('EMAIL_RECEIVER')
    password = os.getenv('EMAIL_PASSWORD')
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))

    if not all([sender, receiver, password]):
        logging.error("이메일 설정이 완료되지 않았습니다.")
        return False

    try:
        msg = MIMEText(message, 'html', 'utf-8')
        msg["Subject"] = f"{TICKER} 상장 알림 {subject_suffix}"
        msg["From"] = sender
        msg["To"] = receiver

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        
        logging.info(f"이메일 알림 발송 완료: {sender} -> {receiver}")
        return True
        
    except Exception as e:
        logging.error(f"이메일 발송 실패: {str(e)}")
        return False

def send_listing_confirmed_email():
    """상장 확인 이메일을 발송합니다."""
    kst_time = get_kst_time()
    utc_time = datetime.datetime.utcnow()
    
    html_message = f"""
    <html>
    <body>
        <h2>🎉 주식 상장 확인!</h2>
        <p><strong>{TICKER}</strong> 상장이 확인되었습니다!</p>
        <div style="background-color: #d4edda; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 5px solid #28a745;">
            <h3>✅ 상장 정보</h3>
            <ul>
                <li><strong>종목 코드:</strong> {TICKER}</li>
                <li><strong>상장 상태:</strong> 활성</li>
                <li><strong>확인 시간 (KST):</strong> {kst_time.strftime('%Y-%m-%d %H:%M:%S')}</li>
                <li><strong>확인 시간 (UTC):</strong> {utc_time.strftime('%Y-%m-%d %H:%M:%S')}</li>
                <li><strong>데이터 소스:</strong> Yahoo Finance</li>
            </ul>
        </div>
        <div style="background-color: #fff3cd; padding: 10px; border-radius: 5px; margin: 10px 0;">
            <strong>📢 모니터링 종료:</strong> 상장이 확인되어 모니터링이 자동으로 종료됩니다.
        </div>
        <p>야후 파이낸스에서 시세 데이터가 확인되었습니다.</p>
        <hr>
        <small>이 알림은 Azure Function App에서 자동으로 발송되었습니다.</small>
    </body>
    </html>
    """
    
    return send_email_alert(html_message, "(상장 확인)")

def send_monitoring_status_email():
    """모니터링 상태 이메일을 발송합니다."""
    kst_time = get_kst_time()
    
    html_message = f"""
    <html>
    <body>
        <h2>⏰ 주식 상장 모니터링 상태</h2>
        <p><strong>{TICKER}</strong> 상장 모니터링이 진행 중입니다.</p>
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0;">
            <h3>📊 모니터링 정보</h3>
            <ul>
                <li><strong>종목 코드:</strong> {TICKER}</li>
                <li><strong>상장 상태:</strong> 아직 상장되지 않음</li>
                <li><strong>확인 시간 (KST):</strong> {kst_time.strftime('%Y-%m-%d %H:%M:%S')}</li>
                <li><strong>모니터링 시간:</strong> 매일 21:30 ~ 다음날 06:00 (KST)</li>
                <li><strong>알림 주기:</strong> 1시간마다</li>
            </ul>
        </div>
        <div style="background-color: #e2e3e5; padding: 10px; border-radius: 5px; margin: 10px 0;">
            <strong>⏳ 다음 알림:</strong> 1시간 후 또는 상장 확인 시
        </div>
        <p>상장이 확인되면 즉시 알림을 발송하고 모니터링을 종료합니다.</p>
        <hr>
        <small>이 알림은 Azure Function App에서 자동으로 발송되었습니다.</small>
    </body>
    </html>
    """
    
    return send_email_alert(html_message, "(모니터링 중)")

def get_stock_data(ticker):
    """yfinance 대신 직접 API를 호출하여 주식 데이터를 가져옵니다."""
    try:
        # Yahoo Finance API 직접 호출
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # API 응답 구조 확인
            if 'chart' in data and 'result' in data['chart'] and len(data['chart']['result']) > 0:
                result = data['chart']['result'][0]
                
                # 메타데이터에서 현재 가격 정보 추출
                if 'meta' in result:
                    meta = result['meta']
                    price = meta.get('regularMarketPrice')
                    currency = meta.get('currency', 'USD')
                    exchange = meta.get('exchangeName', 'Unknown')
                    
                    if price is not None:
                        return {
                            'price': price,
                            'currency': currency,
                            'exchange': exchange,
                            'status': 'active'
                        }
            
            # 데이터가 없으면 상장되지 않은 것으로 간주
            return None
            
        else:
            logging.warning(f"API 호출 실패: HTTP {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        logging.error(f"API 호출 타임아웃: {ticker}")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"API 호출 중 네트워크 오류: {e}")
        return None
    except Exception as e:
        logging.error(f"주식 데이터 조회 중 예상치 못한 오류: {e}")
        return None

def main(mytimer: func.TimerRequest) -> None:
    """Timer Trigger 함수 - 5분마다 실행"""
    global MONITORING_ACTIVE, LISTING_CONFIRMED
    
    # 모니터링이 비활성화된 경우 종료
    if not MONITORING_ACTIVE or LISTING_CONFIRMED:
        logging.info("모니터링이 비활성화되어 있습니다.")
        return
    
    kst_time = get_kst_time()
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    logging.info("Checking FRMI listing status at %s (KST: %s)", 
                utc_timestamp, kst_time.strftime('%Y-%m-%d %H:%M:%S'))

    # 모니터링 시간 확인
    if not is_monitoring_time():
        logging.info("현재 시간은 모니터링 시간이 아닙니다. (21:30 ~ 06:00 KST)")
        return

    try:
        # yfinance 대신 직접 API 호출
        stock_data = get_stock_data(TICKER)
        
        if stock_data and stock_data.get('price') is not None:
            # 상장 확인됨
            logging.info("%s is listed! Price: %s %s. Sending immediate alert and stopping monitoring...", 
                        TICKER, stock_data['price'], stock_data.get('currency', 'USD'))
            
            # 즉시 상장 확인 이메일 발송
            success = send_listing_confirmed_email()
            if success:
                logging.info("상장 확인 이메일이 성공적으로 발송되었습니다.")
                # 모니터링 종료
                MONITORING_ACTIVE = False
                LISTING_CONFIRMED = True
                logging.info("상장이 확인되어 모니터링을 종료합니다.")
            else:
                logging.error("상장 확인 이메일 발송에 실패했습니다.")
        else:
            # 아직 상장되지 않음
            logging.info("%s not listed yet.", TICKER)
            
            # 1시간마다 상태 알림 발송
            if should_send_notification():
                logging.info("1시간 경과 - 모니터링 상태 이메일 발송")
                success = send_monitoring_status_email()
                if success:
                    update_last_notification_time()
                    logging.info("모니터링 상태 이메일이 성공적으로 발송되었습니다.")
                else:
                    logging.error("모니터링 상태 이메일 발송에 실패했습니다.")
            else:
                logging.info("1시간이 경과하지 않아 이메일을 발송하지 않습니다.")
                
    except Exception as e:
        logging.error(f"주식 데이터 조회 중 오류: {str(e)}")