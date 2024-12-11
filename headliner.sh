#!/bin/bash

# Set environment variables
PROJECT_DIR=/app
PYTHON_EXEC=$PROJECT_DIR/.venv/bin/python
MANAGE_PY=$PROJECT_DIR/manage.py

# Run the management command
$PYTHON_EXEC $MANAGE_PY update_headlines
