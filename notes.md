# Installed on Ubuntu 18.04 LTS Windows subsystem
# System updated with the following:

sudo apt update && sudo apt upgrade && sudo apt dist-upgrade

sudo apt install python-pip

pip install --upgrade pip

sudo apt install git

# set Git up to remember your credentials (stored in will be saved in ~/.git-credentials file.) - see https://www.shellhacks.com/git-config-username-password-store-credentials

git config credential.helper store && git config --global credential.helper store


sudo apt-get install cron

sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl

sudo apt-get install -y python3-dev libssl-dev

sudo apt install -y pylint

sudo apt-get install -y python3-venv

curl https://pyenv.run | bash

echo '' >> ~/.bashrc
echo 'export PATH="/home/ubuntu/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
exec "$SHELL"

pyenv install 3.5.3

pip install cookiecutter

pip install singer-python singer-tools target-stitch target-json

# Create then Activate venv with 
python3 -m venv ~/.virtualenvs/tap-bls

source ~/.virtualenvs/tap-bls/bin/activate

pyenv local 3.5.3

pip install --upgrade pip wheel

cd tap-bls 

pip install -e .

tap-bls -c sample_config.json --discover > catalog.json

tap-foobar -c sample_config.json --properties catalog.json

# install tap-csv
python3 -m venv ~/.virtualenvs/target-csv      # create a virtual environment specific to this tap
source ~/.virtualenvs/target-csv/bin/activate  # activate the virtual environment
pyenv local 3.5.3
pip install --upgrade pip wheel
pip install target-csv
deactivate

# run the tap

~/.virtualenvs/tap-bls/bin/tap-bls --config ~/tap-bls-config/config.json | ~/.virtualenvs/target-csv/bin/target-csv


Google Sheets API key:
AIzaSyCvTSJ08CKxpExrbk_itQTWQ8kf1UGqj7M



printf '{"type":"SCHEMA", "stream":"hello","key_properties":[],"schema":{"type":"object", "properties":{"value":{"type":"string"},"name":{"type":"string"},"score":{"type":"integer"}}}}\n{"type":"RECORD","stream":"hello","schema":"hello","record":{"value":"world","name":"james","score":12}}\n{"type":"RECORD","stream":"hello","schema":"hello","record":{"value":"fraser1","name":"bond","score":7}}\n' | ~/.virtualenvs/target-csv/bin/target-csv
