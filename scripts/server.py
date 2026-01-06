"""
Willis Facemap 통합 서버 스크립트 v2.0

- Next.js 서버 실행
- Cloudflare Tunnel (Named Tunnel 또는 Quick Tunnel)
- GitHub 자동 감지 + 자동 재시작

환경변수:
  USE_NAMED_TUNNEL: 'true'면 Named Tunnel 사용 (기본: Quick Tunnel)
  TUNNEL_NAME: Named Tunnel 이름 (기본: facemap)
  PORT: Next.js 포트 (기본: 3000)
  CHECK_INTERVAL: 업데이트 확인 주기 초 (기본: 30)
"""

import subprocess
import time
import sys
import os
import signal
from datetime import datetime

# 설정 (환경변수로 오버라이드 가능)
CHECK_INTERVAL = int(os.environ.get('CHECK_INTERVAL', 30))
TUNNEL_NAME = os.environ.get('TUNNEL_NAME', 'facemap')
PORT = int(os.environ.get('PORT', 3000))
USE_NAMED_TUNNEL = os.environ.get('USE_NAMED_TUNNEL', 'false').lower() == 'true'

# 프로젝트 루트 경로 (scripts/ 폴더의 상위)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
        log(f"[ERROR] Update check failed: {e}")
        return False, None

def pull_updates():
    try:
        log("[PULL] Downloading updates...")
        subprocess.run(['git', 'pull', 'origin', 'main'], check=True, capture_output=True)
        log("[OK] Update complete!")
        return True
    except Exception as e:
        log(f"[ERROR] Update failed: {e}")
        return False

def build_app():
    """Next.js app build"""
    try:
        log("[BUILD] Building app...")
        subprocess.run(
            'yarn workspace @facemap/core build',
            check=True, capture_output=True, shell=True
        )
        subprocess.run(
            'yarn workspace web build',
            check=True, capture_output=True, shell=True
        )
        log("[OK] Build complete!")
        return True
    except Exception as e:
        log(f"[ERROR] Build failed: {e}")
        return False

def start_server():
    global server_process
    log(f"[SERVER] Starting Next.js server (port {PORT})...")

    server_process = subprocess.Popen(
        f'yarn workspace web start -p {PORT}',
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
    )
    time.sleep(3)
    log("[OK] Server started")

def stop_server():
    global server_process
    if server_process:
        log("[SERVER] Stopping server...")
        if os.name == 'nt':
            subprocess.run(['taskkill', '/F', '/T', '/PID', str(server_process.pid)],
                         capture_output=True)
        else:
            os.killpg(os.getpgid(server_process.pid), signal.SIGTERM)
        server_process = None
        time.sleep(2)
        log("[OK] Server stopped")

def start_tunnel():
    global tunnel_process

    # cloudflared 경로 (프로젝트 루트 또는 시스템)
    cloudflared_in_root = os.path.join(PROJECT_ROOT, 'cloudflared.exe')
    cloudflared_path = cloudflared_in_root if os.path.exists(cloudflared_in_root) else 'cloudflared'

    try:
        if USE_NAMED_TUNNEL:
            # Named Tunnel mode (fixed URL)
            log(f"[TUNNEL] Starting Cloudflare Named Tunnel ({TUNNEL_NAME})...")
            tunnel_process = subprocess.Popen(
                [cloudflared_path, 'tunnel', 'run', TUNNEL_NAME],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            # Named Tunnel output watcher
            import threading
            def watch_named_tunnel():
                for line in tunnel_process.stdout:
                    print(f"[Tunnel] {line.strip()}")

            thread = threading.Thread(target=watch_named_tunnel, daemon=True)
            thread.start()

            time.sleep(5)
            log("=" * 60)
            log(f"[OK] Named Tunnel '{TUNNEL_NAME}' started")
            log("    Access via hostname in config.yml")
            log("=" * 60)
        else:
            # Quick Tunnel mode
            log("[TUNNEL] Starting Cloudflare Quick Tunnel...")
            tunnel_process = subprocess.Popen(
                [cloudflared_path, 'tunnel', '--url', f'http://localhost:{PORT}'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            # URL detection thread
            import threading
            def watch_tunnel_output():
                url_file = os.path.join(PROJECT_ROOT, 'TUNNEL_URL.txt')
                for line in tunnel_process.stdout:
                    print(f"[Tunnel] {line.strip()}")
                    # URL detection
                    if 'trycloudflare.com' in line:
                        import re
                        match = re.search(r'https://[a-z0-9-]+\.trycloudflare\.com', line)
                        if match:
                            url = match.group(0)
                            log("=" * 60)
                            log(f"[URL] Tunnel URL: {url}")
                            log("=" * 60)
                            # Save to file
                            with open(url_file, 'w') as f:
                                f.write(url)
                            log(f"[OK] URL saved to TUNNEL_URL.txt")

            thread = threading.Thread(target=watch_tunnel_output, daemon=True)
            thread.start()
            time.sleep(8)

        log("[OK] Tunnel started")

    except FileNotFoundError:
        log("[ERROR] cloudflared not installed")
        return

def restart_server():
    stop_server()
    if build_app():
        start_server()

def cleanup(signum=None, frame=None):
    log("\n[EXIT] Shutting down...")
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
    log("Willis Facemap Server v2.0")
    log("=" * 60)
    log(f"- Port: {PORT}")
    log(f"- GitHub check interval: {CHECK_INTERVAL}s")
    log("- On update: restart server only (tunnel URL preserved!)")
    log("- Press Ctrl+C to exit")
    log("=" * 60)

    # Initial build & start
    if not build_app():
        log("[ERROR] Initial build failed. Exiting.")
        sys.exit(1)

    start_server()
    start_tunnel()

    log("=" * 60)
    log("[OK] Server ready!")
    log("=" * 60)

    # Main loop
    try:
        while True:
            has_updates, remote = check_for_updates()

            if has_updates:
                log("=" * 60)
                log(f"[UPDATE] New update found! ({remote[:8]})")
                log("=" * 60)

                if pull_updates():
                    restart_server()
                    log("=" * 60)
                    log("[OK] Update applied! (tunnel URL preserved)")
                    log("=" * 60)
            else:
                log("[CHECK] Up to date")

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    # Change to project root
    os.chdir(PROJECT_ROOT)

    # Git check
    if not os.path.exists('.git'):
        print("[ERROR] Not a git repository")
        sys.exit(1)

    main()
