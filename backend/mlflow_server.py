#!/usr/bin/env python3
"""Script untuk menjalankan MLflow tracking server"""

import subprocess
import sys

if __name__ == "__main__":
    print("🚀 Starting MLflow tracking server...")
    print("📊 UI akan tersedia di http://localhost:5000")
    subprocess.run([
        sys.executable, "-m", "mlflow", "server",
        "--host", "127.0.0.1",
        "--port", "5000",
        "--backend-store-uri", "file:mlruns",
        "--default-artifact-root", "file:mlruns"
    ])