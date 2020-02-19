# [Code Clusters Models](https://github.com/Aalto-LeTech/CodeClustersModeling)

Repository for the models used by the [CodeClusters](https://github.com/Aalto-LeTech/CodeClusters)

We are using Jupyter to prototyping our models.

## How to install

You should have Python >=3.5 installed, pyenv or mkvirtualenv for creating virtual environments.

1. Generate virtual environment eg: `mkvirtualenv cc`
2. Install requirements: `pip install -r dev-requirements.txt`
3. Due to some weird unimaginable things, installation of psycopg2 didn't work directly on macOS. So following this [thread](https://stackoverflow.com/questions/26288042/error-installing-psycopg2-library-not-found-for-lssl) what I had to do was: `env LDFLAGS="-I/usr/local/opt/openssl/include -L/usr/local/opt/openssl/lib" pip install psycopg2`. But first try just `pip install psycopg2` to see if it works
4. Copy the example environment variables: `cp .example.env .env`
5. Launch the notebook: `jupyter notebook`
6. In http://localhost:8888 open the `notebooks` folder to find the models

You can install new dependencies without stopping the notebook, just open another terminal and remember to activate the virtualenv eg: `workon cc`. Then just use pip: `pip install tensorflow`. **Remember** to save the new library if you use it in some models: `pip freeze > dev-requirements.txt`

## How to install server

The same prerequisites as in the notebook-setup.

1. Generate virtual environment eg: `mkvirtualenv cc-app`
2. Install requirements: `pip install -r app-requirements.txt`
3. Due to some weird unimaginable things, installation of psycopg2 didn't work directly on macOS. So following this [thread](https://stackoverflow.com/questions/26288042/error-installing-psycopg2-library-not-found-for-lssl) what I had to do was: `env LDFLAGS="-I/usr/local/opt/openssl/include -L/usr/local/opt/openssl/lib" pip install psycopg2`. But first try just `pip install psycopg2` to see if it works
4. Copy the example environment variables if you haven't already: `cp .example.env .env`
5. Launch the dev-ser with: `./dev.sh` NOTE: there is some problems with Flask not triggering properly on code changes