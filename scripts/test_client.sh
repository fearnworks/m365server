source venv/bin/activate
cd ./m365client
pip install -r requirements/requirements.txt -q 
# pip install -r requirements/requirements-dev.txt -q 
pip install -e . -q 
pytest .
cd ..


