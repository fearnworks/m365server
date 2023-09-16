python3 -m venv venv 
source ./venv/bin/activate
pip install -e ./m365server --upgrade
pip install -e ./m365client --upgrade
bash ./scripts/run_tests.sh