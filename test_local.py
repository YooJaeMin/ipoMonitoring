#!/usr/bin/env python3
"""
로컬에서 주식 모니터링을 테스트하는 스크립트
"""

import logging
import time
from init import main

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('stock_monitor.log')
    ]
)

def run_monitoring():
    """주식 모니터링을 실행합니다."""
    logging.info("=== 주식 모니터링 시작 ===")
    
    try:
        # main 함수 호출 (Azure Functions Timer 없이)
        main()
        logging.info("=== 주식 모니터링 완료 ===")
    except Exception as e:
        logging.error(f"모니터링 실행 중 오류: {e}")

if __name__ == "__main__":
    # 환경 변수 설정 (실제 값으로 변경 필요)
    import os
    os.environ.setdefault('EMAIL_SENDER', 'your-email@gmail.com')
    os.environ.setdefault('EMAIL_RECEIVER', 'recipient@example.com')
    os.environ.setdefault('EMAIL_PASSWORD', 'your-app-password')
    os.environ.setdefault('SMTP_SERVER', 'smtp.gmail.com')
    os.environ.setdefault('SMTP_PORT', '587')
    
    # 모니터링 실행
    run_monitoring()