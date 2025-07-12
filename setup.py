from setuptools import setup, find_packages

setup(
    name="label-router",
    version="0.1.0",
    description="Intelligent Label System for Construction Meeting Transcripts",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "pydantic>=2.5.2",
        "sentence-transformers>=2.2.2",
        "numpy>=1.24.3",
        "scikit-learn>=1.3.2",
        "mecab-python3>=1.0.6",
        "unidic-lite>=1.0.8",
        "faiss-cpu>=1.7.4",
        "sqlalchemy>=2.0.23",
        "sqlite-utils>=3.35.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "black>=23.11.0",
            "flake8>=6.1.0",
        ],
        "ui": [
            "gradio>=4.8.0",
        ],
    },
)