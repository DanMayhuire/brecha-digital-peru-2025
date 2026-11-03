"""Execute the current scientific notebooks; never import an older teacher run."""
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    subprocess.run([sys.executable,str(ROOT/"src/execute_notebooks.py")],cwd=ROOT,check=True)
