"""
Setup script for QR Code Bot (optional, for package installation).
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="qr-code-bot",
    version="2.0.0",
    author="QR Code Bot Team",
    description="Telegram bot for generating QR codes from Excel files and text messages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "python-telegram-bot>=20.7",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "python-dotenv>=1.0.0",
        "sqlalchemy>=2.0.23",
        "alembic>=1.13.0",
        "pandas>=2.1.4",
        "openpyxl>=3.1.2",
        "xlrd>=2.0.1",
        "qrcode[pil]>=7.4.2",
        "Pillow>=10.1.0",
        "fpdf2>=2.7.6",
    ],
)

