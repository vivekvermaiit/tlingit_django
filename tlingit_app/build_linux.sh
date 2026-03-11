#!/bin/bash
docker run --platform linux/amd64 \
  -v "$(pwd)/..":/project \
  -w /project/tlingit_app \
  python:3.11 bash -c "
    pip install pyinstaller -r /project/requirements.txt &&
    pyinstaller --onefile manage.py --name tlingit_backend \
      --add-data 'corpus/templates:corpus/templates' \
      --add-data 'corpus/static:corpus/static' \
      --add-data 'corpus/templatetags:corpus/templatetags' \
      --add-data 'db.sqlite3:.' \
  "