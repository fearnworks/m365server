# check if environment is PRODUCTION or DEVELOPMENT
if [ "$ENVIRONMENT" = "PRODUCTION" ]; then
  echo "Running Production Server"
  python3 -m pip install -e .
  uvicorn m365server.main:app --host 0.0.0.0 --port $M365_SERVER_PORT 

else
    echo "Running Development Server"
    cd /code 
    python3 -m pip install -e .
    uvicorn m365server.main:app --host 0.0.0.0 --port $M365_SERVER_PORT --reload
fi