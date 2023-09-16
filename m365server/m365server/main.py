from fastapi import FastAPI
import redis
from loguru import logger 
from dotenv import load_dotenv, find_dotenv
from m365server.api.api import api_router
import uvicorn


load_dotenv(find_dotenv())
app = FastAPI()
app.include_router(api_router, prefix="/api/v1")

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))


if __name__ == "__main__":
    logger.info('Starting server')
    uvicorn.run(app, host="0.0.0.0", port=12000, log_level="debug")
