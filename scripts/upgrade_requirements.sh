#!/bin/bash
cd ./m365server
pip-compile requirements/requirements.in --upgrade
pip-compile requirements/requirements-dev.in --upgrade
pip-compile requirements/requirements-test.in --upgrade
echo "Pin update complete."
cd ..

cd ./m365client
pip-compile requirements/requirements.in --upgrade
# pip-compile requirements/requirements-dev.in --upgrade
pip-compile requirements/requirements-test.in --upgrade
echo "Pin update complete."
cd ..
