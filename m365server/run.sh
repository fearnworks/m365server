cd /code 
python3 -m pip install -e .
uvicorn m365server.main:app --host 0.0.0.0 --port 17200 --reload