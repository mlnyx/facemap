"""
Willis Facemap 통합 서버 스크립트

- Next.js 서버 실행
- Cloudflare Tunnel (Named Tunnel로 고정 URL)
- GitHub 자동 감지 + 자동 재시작
"""

import subprocess
import time
import sys
import os
import signal
from datetime import datetime

# 설정
CHECK_INTERVAL = 30  # 초
TUNNEL_NAME = "facemap"  # Cloudflare Named Tunnel 이름
PORT = 3000

# 프로세스 관리
server_process = None
tunnel_process = None

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def get_current_commit():
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except:
        return None

def check_for_updates():
    try:
        subprocess.run(['git', 'fetch'], check=True, capture_output=True)
        result = subprocess.run(
            ['git', 'rev-parse', 'origin/main'],
            capture_output=True, text=True, check=True
        )
        remote = result.stdout.strip()
        local = get_current_commit()
        return remote != local, remote
    except Exception as e:
        log(f"업데이트 확인 실패: {e}")
        return False, None

def pull_updates():
    try:
        log("📥 업데이트 다운로드 중...")
        subprocess.run(['git', 'pull', 'origin', 'main'], check=True, capture_output=True)
        log("✅ 업데이트 완료!")
        return True
    except Exception as e:
        log(f"❌ 업데이트 실패: {e}")
        return False

def build_app():
    """Next.js 앱 빌드"""
    try:
        log("🔨 앱 빌드 중...")
        subprocess.run(
            ['yarn', 'workspace', '@facemap/core', 'build'],
            check=True, capture_output=True
        )
        subprocess.run(
            ['yarn', 'workspace', 'web', 'build'],
            check=True, capture_output=True
        )
        log("✅ 빌드 완료!")
        return True
    except Exception as e:
        log(f"❌ 빌드 실패: {e}")
        return False

def start_server():
    global server_process
    log(f"🚀 Next.js 서버 시작 (포트 {PORT})...")

    server_process = subprocess.Popen(
        ['yarn', 'workspace', 'web', 'start', '-p', str(PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
    )
    time.sleep(3)
    log("✅ 서버 시작됨")

def stop_server():
    global server_process
    if server_process:
        log("🛑 서버 중지 중...")
        if os.name == 'nt':
            subprocess.run(['taskkill', '/F', '/T', '/PID', str(server_process.pid)],
                         capture_output=True)
        else:
            os.killpg(os.getpgid(server_process.pid), signal.SIGTERM)
        server_process = None
        time.sleep(2)
        log("✅ 서버 중지됨")

def start_tunnel():
    global tunnel_process
    log("🌐 Cloudflare Tunnel 시작...")

    # cloudflared 경로 (프로젝트 폴더 또는 시스템)
    cloudflared_path = './cloudflared.exe' if os.path.exists('./cloudflared.exe') else 'cloudflared'

    try:
        tunnel_process = subprocess.Popen(
            [cloudflared_path, 'tunnel', '--url', f'http://localhost:{PORT}'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        # URL 감지 스레드 시작
        import threading
        def watch_tunnel_output():
            url_file = os.path.join(os.path.dirname(__file__), 'TUNNEL_URL.txt')
            for line in tunnel_process.stdout:
                print(f"[Tunnel] {line.strip()}")
                # URL 감지
                if 'trycloudflare.com' in line:
                    import re
                    match = re.search(r'https://[a-z0-9-]+\.trycloudflare\.com', line)
                    if match:
                        url = match.group(0)
                        log("=" * 60)
                        log(f"🌍 터널 URL: {url}")
                        log("=" * 60)
                        # 파일에 저장
                        with open(url_file, 'w') as f:
                            f.write(url)
                        log(f"📄 URL이 TUNNEL_URL.txt에 저장됨")

        thread = threading.Thread(target=watch_tunnel_output, daemon=True)
        thread.start()

    except FileNotFoundError:
        log("❌ cloudflared가 설치되어 있지 않습니다")
        return

    time.sleep(8)
    log("✅ Tunnel 시작됨")

def restart_server():
    stop_server()
    if build_app():
        start_server()

def cleanup(signum=None, frame=None):
    log("\n🛑 종료 중...")
    stop_server()
    if tunnel_process:
        tunnel_process.terminate()
    sys.exit(0)

def main():
    # Ctrl+C 핸들러
    signal.signal(signal.SIGINT, cleanup)
    if os.name != 'nt':
        signal.signal(signal.SIGTERM, cleanup)

    log("=" * 60)
    log("Willis Facemap 통합 서버")
    log("=" * 60)
    log(f"• GitHub 변경사항 {CHECK_INTERVAL}초마다 확인")
    log("• 변경 감지 시 자동 빌드 & 재시작")
    log("• Ctrl+C로 종료")
    log("=" * 60)

    # 초기 빌드 & 시작
    if not build_app():
        log("❌ 초기 빌드 실패. 종료합니다.")
        sys.exit(1)

    start_server()
    start_tunnel()

    log("=" * 60)
    log("🎉 서버 준비 완료!")
    log("=" * 60)

    # 메인 루프
    try:
        while True:
            has_updates, remote = check_for_updates()

            if has_updates:
                log("=" * 60)
                log(f"🔔 새 업데이트 발견! ({remote[:8]})")
                log("=" * 60)

                if pull_updates():
                    restart_server()
                    log("=" * 60)
                    log("🎉 업데이트 적용 완료!")
                    log("=" * 60)
            else:
                log(f"✓ 최신 상태")

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Git 확인
    if not os.path.exists('.git'):
        print("❌ Git 저장소가 아닙니다")
        sys.exit(1)

    main()
