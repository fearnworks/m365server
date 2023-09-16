source venv/bin/activate
cd ./m365server
pip install azure-core
pip install azure-storage-blob
pip install -r requirements/requirements.txt -q 
pip install -r requirements/requirements-dev.txt -q 
pip install -e . -q
pytest .
