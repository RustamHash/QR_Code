"""
Точка входа в приложение.
"""
import sys
from pathlib import Path

# Добавляем путь к src в PYTHONPATH
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from src.bot.main import main

if __name__ == "__main__":
    main()

