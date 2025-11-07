import os
import sys

# Caminho absoluto da pasta backend
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

os.chdir(backend_path)
os.system('python run.py')
