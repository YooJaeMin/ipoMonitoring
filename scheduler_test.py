import schedule
import time
import datetime
import pytz
from test_local import check_stock_listing, get_kst_time, is_monitoring_time

def run_monitoring():
    """모니터링 함수 실행"""
    kst_time = get_kst_time()
    print(f"\n🕐 {kst_time.strftime('%Y-%m-%d %H:%M:%S')} (KST) - 모니터링 실행")
    
    # 모니터링 시간 확인
    if is_monitoring_time():
        print("✅ 모니터링 시간입니다.")
        check_stock_listing()
    else:
        print("⏰ 모니터링 시간이 아닙니다. (21:30 ~ 06:00 KST)")
        print("다음 모니터링 시간까지 대기합니다...")

if __name__ == "__main__":
    print("🚀 FRMI 주식 상장 모니터링 스케줄러 시작")
    print("=" * 60)
    
    kst_time = get_kst_time()
    print(f"현재 시간 (KST): {kst_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"모니터링 시간: 매일 21:30 ~ 다음날 06:00 (KST)")
    print(f"알림 주기: 1시간마다 (상장되지 않았을 때)")
    print(f"상장 확인 시: 즉시 알림 + 모니터링 종료")
    print("=" * 60)
    print("Ctrl+C로 종료하세요.")
    
    # 5분마다 실행 (모니터링 시간 내에서만 실제 작업)
    schedule.every(5).minutes.do(run_monitoring)
    
    # 즉시 한 번 실행
    run_monitoring()
    
    # 스케줄러 실행
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 모니터링을 종료합니다.")
