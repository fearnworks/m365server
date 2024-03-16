from dotenv import load_dotenv, find_dotenv
import httpx
from loguru import logger
import httpx
import pandas as pd
import io
from typing import Callable, List, Dict
import os

### Backwards compat

from m365client.handlers import *

load_dotenv(find_dotenv())








