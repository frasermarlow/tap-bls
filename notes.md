# Installed on Ubuntu 18.04 LTS Windows subsystem
# System updated with the following:

sudo apt update && sudo apt upgrade && sudo apt dist-upgrade

sudo apt install python-pip

pip install --upgrade pip

sudo apt install git

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

# Create then Activate venv with 
source ~/.venvs/tap_bls/bin/activate
