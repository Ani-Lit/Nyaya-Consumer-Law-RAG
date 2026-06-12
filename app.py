import subprocess
import sys

subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend/app.py", "--server.port", "7860", "--server.address", "0.0.0.0"]) 

