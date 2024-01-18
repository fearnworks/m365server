if [ ! -d "venv" ]; then
  python3 -m venv venv 
fi

source ./venv/bin/activate
python3 -m pip install pip --upgrade 
pip install pip-tools --upgrade
pip install -e ./m365server[dev,test] --upgrade
pip install -e ./m365client --upgrade
bash ./scripts/run_tests.sh

if [ -z "$(docker network ls | grep hq-network)" ]; then
  docker network create hq-network
fi

docker compose up 