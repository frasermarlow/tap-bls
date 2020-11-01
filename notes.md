# Installed on Ubuntu 18.04 LTS Windows subsystem
# System updated with the following:

sudo apt update && sudo apt upgrade && sudo apt dist-upgrade

sudo apt install python-pip

pip install --upgrade pip

sudo apt install git

git clone https://github.com/frasermarlow/tap-bls

#### After you clone the directory, set Git up to remember your credentials (stored in will be saved in ~/.git-credentials file.) - see https://www.shellhacks.com/git-config-username-password-store-credentials

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

deactivate # exit the virtual environment

> Note that I create the config file in a separate directory, and not in the tap.

~/.virtualenvs/tap-bls/bin/tap-bls --config ~/tap-bls-config/config.json --discover > catalog.json

~/.virtualenvs/tap-bls/bin/tap-bls --config ~/tap-bls-config/config.json --properties catalog.json

~/.virtualenvs/tap-bls/bin/tap-bls --config ~/tap-bls-config/config.json --discover


# install tap-csv
python3 -m venv ~/.virtualenvs/target-csv      # create a virtual environment specific to this tap
source ~/.virtualenvs/target-csv/bin/activate  # activate the virtual environment
pyenv local 3.5.3
pip install --upgrade pip wheel
pip install target-csv
deactivate

# run the tap

~/.virtualenvs/tap-bls/bin/tap-bls --config ~/tap-bls-config/config.json | ~/.virtualenvs/target-csv/bin/target-csv
