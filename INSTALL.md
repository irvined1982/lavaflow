# Install

A basic set of install instructions to get you started.

## The code

```bash
git clone https://github.com/irvined1982/lavaflow.git
```

### Virtualenv - a virtual ennvironment

[Virtualenv](http://www.virtualenv.org/en/latest/) allows the creation of an 
isolated Python environment, for development, testing or production purposes. 
If this is not already installed, installation using pip is suggested.

## Bootstrap script

Using a virtual environment encapsulates the dependency tree to the directory 
and environment in use. A bootstrap script provides for all this in two simple 
commands

```bash
python lavaflow-venv.py
python lavaflow-bootstrap.py /tmp/lavaflow
```

Assuming this is successful the ```/tmp/lavaflow``` directory will contain a 
copy of the repository and a virtualenv to run it with:

```bash
drwxr-xr-x 5 503 503 4096 Apr  8 15:53 lavaflow
drwxr-xr-x 5 503 503 4096 Apr  8 15:54 lavaflow-env
```

An important file ```lavaflow-env/bin/post_activate``` will have been generated 
which will require editing depending on your local setup, otherwise the defaults
will be used.  The additions need to appear as, where the value of the variables
match those to be used.

```bash
export LAVAFLOW_DBNAME=<database-name>
export LAVAFLOW_DBHOST=<database-host>
export LAVAFLOW_DBPORT=<database-port>
export LAVAFLOW_DBUSER=<database-user>
export LAVAFLOW_DBPASS=<database-pass>
```

It will already contain the ```LAVAFLOW_ROOT``` variable - set in this case 
to ```/tmp/lavaflow/lavaflow```

### Database

*To be written*

## Boot

```bash
source lavaflow-env/bin/activate
python lavaflow/manage.py runserver 0.0.0.0:8080
```

