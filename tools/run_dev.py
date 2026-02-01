"""
Moon AI Development Server
Runs both FastAPI backend and SvelteKit frontend.
"""

import os
import signal
import subprocess
import sys
from pathlib import Path


def get_local_ip():
    """Get local network IP address."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"


def kill_port(port: int):
    """Kill process using a port."""
    try:
        result = subprocess.run(
            f"lsof -ti:{port} | xargs kill -9 2>/dev/null",
            shell=True,
            capture_output=True
        )
    except Exception:
        pass


def run_dev_server(mode: str = "all"):
    """
    Run development servers.
    
    Args:
        mode: 'all' (default), 'api', or 'web'
    """
    root = Path.cwd()
    frontend_dir = root / "frontend"
    
    # Validate paths
    if not (root / "api" / "main.py").exists():
        print("\033[0;31m[ERROR] api/main.py not found.\033[0m")
        return
    
    if mode in ["all", "web"] and not frontend_dir.exists():
        print("\033[0;31m[ERROR] frontend/ directory not found.\033[0m")
        return
    
    # Kill existing processes
    print("[INFO] Cleaning up ports...")
    kill_port(8000)
    kill_port(5173)
    kill_port(5174)
    
    processes = []
    local_ip = get_local_ip()
    
    try:
        # Start API server
        if mode in ["all", "api"]:
            print("[INFO] Starting FastAPI backend on :8000...")
            api_proc = subprocess.Popen(
                ["uvicorn", "api.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
                cwd=root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            processes.append(("API", api_proc))
        
        # Start Frontend server
        if mode in ["all", "web"]:
            print("[INFO] Starting SvelteKit frontend on :5173...")
            web_proc = subprocess.Popen(
                ["pnpm", "dev", "--host"],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            processes.append(("Web", web_proc))
        
        # Print access info
        print("\n" + "=" * 50)
        print("\033[1;32m✓ Moon AI Development Servers Running\033[0m")
        print("=" * 50)
        print(f"\n  Local:   http://localhost:5173")
        print(f"  Network: http://{local_ip}:5173")
        print(f"  API:     http://{local_ip}:8000/api/health")
        print(f"\n  Press Ctrl+C to stop all servers")
        print("=" * 50 + "\n")
        
        # Stream output from both processes
        import select
        
        while True:
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"\033[0;31m[{name}] Process exited\033[0m")
                    raise KeyboardInterrupt
                
                # Non-blocking read
                if proc.stdout:
                    import fcntl
                    fd = proc.stdout.fileno()
                    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
                    try:
                        line = proc.stdout.readline()
                        if line:
                            print(f"[{name}] {line.decode().strip()}")
                    except Exception:
                        pass
            
            import time
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\n[INFO] Stopping servers...")
        for name, proc in processes:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
        print("[INFO] All servers stopped.")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode not in ["all", "api", "web"]:
        print("Usage: dev [all|api|web]")
        print("  all - Start both API and frontend (default)")
        print("  api - Start only FastAPI backend")
        print("  web - Start only SvelteKit frontend")
        sys.exit(1)
    run_dev_server(mode)
