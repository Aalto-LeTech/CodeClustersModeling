# [Code Clusters Models](https://github.com/Aalto-LeTech/CodeClustersModeling)

Repository for the models used by the [CodeClusters](https://github.com/Aalto-LeTech/CodeClusters)

We are using Jupyter to prototyping our models.

## How to install locally

You should have Python >=3.5 installed, pyenv or mkvirtualenv for creating virtual environments. Also you need Java JDK >=11 to be able to run Checkstyle Java library to generate metrics. **NOTE:** as of 5.8.2022 the `dev-requirements.txt` were not updated although `requirements.txt` were. `psycopg2` might work better now but the situation is still not ideal regarding Python's package management.

1. Generate virtual environment eg: `mkvirtualenv cc`
2. Install requirements: `pip install -r dev-requirements.txt`
3. Due to some weird unimaginable things, installation of psycopg2 didn't work directly on macOS. So following this [thread](https://stackoverflow.com/questions/26288042/error-installing-psycopg2-library-not-found-for-lssl) what I had to do was: `env LDFLAGS="-I/usr/local/opt/openssl/include -L/usr/local/opt/openssl/lib" pip install psycopg2`. But first try just `pip install psycopg2` to see if it works
4. Install Checkstyle to `./tmp`: `mkdir tmp && cd tmp && curl -OL https://github.com/checkstyle/checkstyle/releases/download/checkstyle-10.3.2/checkstyle-10.3.2-all.jar && cd ..`
5. Copy the example environment variables: `cp .example.env .env`
6. Launch the notebook: `jupyter notebook`
7. In http://localhost:8888 open the `notebooks` folder to find the models
8. You can also start the model server with: `./dev.sh` NOTE: there is some problems with Flask not triggering properly on code changes

You can install new dependencies without stopping the notebook, just open another terminal and remember to activate the virtualenv eg: `workon cc`. Then just use pip: `pip install tensorflow`. **Remember** to save the new library if you use it in some models: `pip freeze > dev-requirements.txt`

## How to install with Docker

This is the setup used for production.

1. Copy the example env: `cp .modeling.env.example .modeling.env`. Change variables if necessary
2. Build the image: `docker-compose -f prod-docker-compose.yml build`
3. Start it: `docker-compose -f prod-docker-compose.yml up`

## Installing ANTLR

I have already added the required files to run ANTLR locally, but if you for some reason need to reinstall ANTLR this is how I did it (1.8.2022).

```bash
# Executed with macOS Big Sur

# needs Java 11
brew install openjdk@11
sudo ln -sfn /opt/homebrew/opt/openjdk@11/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk-11.jdk

# Download the JAR file
wget http://www.antlr.org/download/antlr-4.8-complete.jar
wget https://raw.githubusercontent.com/antlr/grammars-v4/master/java/java/JavaLexer.g4
wget https://raw.githubusercontent.com/antlr/grammars-v4/master/java/java/JavaParser.g4
java -jar ./antlr-4.8-complete.jar -Dlanguage=Python3 ./JavaLexer.g4
java -jar ./antlr-4.8-complete.jar -Dlanguage=Python3 ./JavaParser.g4
```
