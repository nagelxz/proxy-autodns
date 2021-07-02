#!/bin/bash

command -v python3 >/dev/null 2>&1 || { 
    echo >&2 "I require python3 but it's not installed.  Aborting. please install python3 and python3-venv"; 
    exit 1; 
}

py_env=`pwd`"/dns-env"

if [ ! -d "dns-env/bin" ]; then 
    mkdir -p "$py_env"
    python3 -m venv "$py_env"
fi

source "$py_env"/bin/activate

which python
python -m pip install -r requirements.txt

python create_dns.py

deactivate