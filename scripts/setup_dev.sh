python3 -m venv venv 
source ./venv/bin/activate
python3 -m pip install pip --upgrade 
pip install -e ./m365server --upgrade
pip install -e ./m365client --upgrade
bash ./scripts/run_tests.sh
docker network create hq-network
docker compose up --build 