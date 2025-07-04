#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI entry point for the Flask application
Used by Gunicorn and other WSGI servers
"""

import os
from app import app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)