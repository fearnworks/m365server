# check if environment is PRODUCTION or DEVELOPMENT
if [ "$ENVIRONMENT" = "PRODUCTION" ]; then
  python3 -m pip install -e .
  echo "Running Production Server"
  echo "Running on port $M365_SERVER_PORT"
  uvicorn m365server.main:app --host 0.0.0.0 --port $M365_SERVER_PORT 

else
    cd /code 
    python3 -m pip install -e .
    echo "Running Development Server"
    echo "Running on port $M365_SERVER_PORT"

    uvicorn m365server.main:app --host 0.0.0.0 --port $M365_SERVER_PORT --reload
fi