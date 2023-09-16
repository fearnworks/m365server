To run :

Fill out .envtemplate variables for your m365 environment under the required header and rename the file .env 

```
docker compose up 
```

To set up a dev environment navigate to the root dir: 

```
./scripts/setup_dev.sh
```

This will create a virtual environment in the venv dir of the root and install both m365client and m365server libs to it. 
It will also run the test suite for these projects to ensure they are hooked up correctly. 

