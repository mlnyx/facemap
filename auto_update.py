"""
Willis Facemap 자동 업데이트 & 재시작 스크립트

GitHub에서 변경사항을 자동으로 감지하고 서버를 재시작합니다.
"""

import subprocess
import time
import sys
import os
from datetime import datetime

def log(message):
    """로그 출력"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def get_current_commit():
    """현재 커밋 해시 가져오기"""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def check_for_updates():
    """GitHub에서 업데이트 확인"""
    try:
        # 원격 저장소 정보 가져오기
        subprocess.run(['git', 'fetch'], check=True, capture_output=True)
        
        # 로컬과 원격 비교
        result = subprocess.run(
            ['git', 'rev-parse', 'origin/main'],
            capture_output=True,
            text=True,
            check=True
        )
        remote_commit = result.stdout.strip()
        local_commit = get_current_commit()
        
        return remote_commit != local_commit, remote_commit
    except subprocess.CalledProcessError as e:
        log(f"업데이트 확인 실패: {e}")
        return False, None

def pull_updates():
    """Git pull 실행"""
    try:
        log("업데이트 다운로드 중...")
        result = subprocess.run(
            ['git', 'pull', 'origin', 'main'],
            capture_output=True,
            text=True,
            check=True
        )
        log("✓ 업데이트 완료!")
        return True
    except subprocess.CalledProcessError as e:
        log(f"업데이트 실패: {e}")
        return False

def restart_server():
    """서버 재시작"""
    log("서버 재시작 중...")
    log("※ 수동으로 Ctrl+C 후 start_tunnel.bat 재실행하세요")
    log("   또는 이 스크립트를 종료하고 서버를 수동 재시작하세요")
    return True

def main():
    """메인 루프"""
    log("=" * 60)
    log("Willis Facemap 자동 업데이트 시작")
    log("=" * 60)
    log("GitHub 저장소를 30초마다 확인합니다")
    log("Ctrl+C로 종료")
    log("=" * 60)
    
    check_interval = 30  # 30초마다 확인
    
    try:
        while True:
            has_updates, remote_commit = check_for_updates()
            
            if has_updates:
                log("🔔 새 업데이트 발견!")
                log(f"   원격 커밋: {remote_commit[:8]}")
                
                if pull_updates():
                    log("=" * 60)
                    log("⚠️  서버를 재시작해야 적용됩니다!")
                    log("   1. 현재 실행 중인 서버 종료 (Ctrl+C)")
                    log("   2. start_tunnel.bat 재실행")
                    log("=" * 60)
                    
                    # 자동 종료 (사용자가 재시작하도록)
                    time.sleep(5)
                    log("자동 업데이트 스크립트를 종료합니다")
                    sys.exit(0)
            else:
                current_time = datetime.now().strftime("%H:%M:%S")
                log(f"✓ 최신 상태 유지 중 ({current_time})")
            
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        log("\n자동 업데이트 종료")
        sys.exit(0)

if __name__ == "__main__":
    # Git이 설치되어 있는지 확인
    try:
        subprocess.run(['git', '--version'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("오류: Git이 설치되어 있지 않습니다")
        print("https://git-scm.com/downloads 에서 설치하세요")
        sys.exit(1)
    
    # Git 저장소인지 확인
    if not os.path.exists('.git'):
        print("오류: Git 저장소가 아닙니다")
        print("git clone으로 다운로드한 폴더에서 실행하세요")
        sys.exit(1)
    
    main()
