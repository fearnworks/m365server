# check if environment is PRODUCTION or DEVELOPMENT
if [ "$ENVIRONMENT" = "PRODUCTION" ]; then
  echo "Running Production Server"
  echo "Running on port $M365_SERVER_PORT"
  uvicorn m365server.main:app --host 0.0.0.0 --port $M365_SERVER_PORT 

else
    cd /code 
    echo "Running Development Server"
    echo "Running on port $M365_SERVER_PORT"

    uvicorn m365server.main:app --host 0.0.0.0 --port $M365_SERVER_PORT --reload
fi