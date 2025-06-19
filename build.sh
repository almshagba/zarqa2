#!/usr/bin/env bash
# Render Build Script
# This script runs during the build phase on Render

set -o errexit  # Exit on error

echo "🚀 Starting build process for Employee Management System..."
echo "📅 Build started at: $(date)"

# Show Python version
echo "🐍 Python version:"
python --version

# Set environment variables to prevent compilation issues
export PANDAS_NO_BUILD_ISOLATION=1
export NUMPY_NO_BUILD_ISOLATION=1

# Upgrade pip and build tools for Python 3.13 compatibility
echo "📦 Upgrading pip and build tools..."
pip install --upgrade pip setuptools wheel

# Install Python dependencies with optimizations
echo "📚 Installing Python dependencies..."

# Install numpy first (pandas dependency) - Python 3.13 compatible
echo "🔢 Installing numpy..."
pip install --only-binary=all numpy==1.26.4

# Install pandas with pre-compiled binaries - Python 3.13 compatible
echo "🐼 Installing pandas..."
pip install --only-binary=all pandas==2.2.3

# Install remaining dependencies
echo "📦 Installing remaining dependencies..."
pip install -r requirements.txt --only-binary=:all: || pip install -r requirements.txt

# Verify critical imports
echo "✅ Verifying installations..."
python -c "import flask; print(f'✓ Flask version: {flask.__version__}')"
python -c "import sqlalchemy; print(f'✓ SQLAlchemy version: {sqlalchemy.__version__}')"
python -c "import numpy; print(f'✓ NumPy version: {numpy.__version__}')"
python -c "import pandas; print(f'✓ Pandas version: {pandas.__version__}')"
python -c "import gunicorn; print('✓ Gunicorn installed successfully')"

# Test app import
echo "🧪 Testing app import..."
python -c "from app import app; print('✓ App imported successfully')"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p static/uploads/forms
mkdir -p static/uploads/temp
mkdir -p instance
mkdir -p logs

# Set proper permissions
echo "🔐 Setting permissions..."
chmod -R 755 static/
chmod +x wsgi.py

# Verify directory structure
echo "📋 Directory structure:"
ls -la static/

# Clean up cache
echo "🧹 Cleaning up..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

echo "✅ Build completed successfully!"
echo "🎉 Ready for deployment..."
echo "📅 Build finished at: $(date)"