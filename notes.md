# Installed on Ubuntu 18.04 LTS Windows subsystem
# System updated with the following:

sudo apt update && sudo apt upgrade && sudo apt dist-upgrade  
sudo apt install python3-pip  
sudo apt install git  
# git config credential.helper store && git config --global credential.helper store  
sudo apt-get install cron  
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl  
sudo apt-get install -y python3-dev libssl-dev pylint 
sudo apt-get install -y python3-venv  
curl https://pyenv.run | bash  
echo '' >> ~/.bashrc  
echo 'export PATH="/home/ubuntu/.pyenv/bin:$PATH"' >> ~/.bashrc  
echo 'eval "$(pyenv init -)"' >> ~/.bashrc  
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc  
exec "$SHELL"  

pyenv install 3.5.3  
python3 --version # you may need to change the next lines based on your version - here I assume 3.6
python3.6 -m pip install cookiecutter  
python3.6 -m pip install singer-python singer-tools target-stitch target-json  

# Install, Create then Activate venv with 
sudo apt-get install python3-venv  
python3 -m venv ~/.virtualenvs/tap-bls  
source ~/.virtualenvs/tap-bls/bin/activate  
pyenv local 3.5.3  
pip install --upgrade pip wheel  
pip install tap-bls  
deactivate # exit the virtual environment  

# create the config directory: 
mkdir tap-bls-config && cd tap-bls-config

# Copy over series.json and sample-catalog.json
curl -H 'Accept: application/vnd.github.v3.raw' -O -L https://raw.githubusercontent.com/frasermarlow/tap-bls/master/series.json
curl -H 'Accept: application/vnd.github.v3.raw' -O -L https://raw.githubusercontent.com/frasermarlow/tap-bls/master/sample_config.json
mv sample_config.json config.json

# EDIT CONFIG AND ADD YOUR KEY

# now we can build the catalog - I use 'tap-foo-config' to store a tap's config, catalog and state, so note this is NOT the tap's root directory.  
~/.virtualenvs/tap-bls/bin/tap-bls --config ~/tap-bls-config/config.json --discover > catalog.json    

# install tap-csv
python3 -m venv ~/.virtualenvs/target-csv      # create a virtual environment specific to this tap  
source ~/.virtualenvs/target-csv/bin/activate  # activate the virtual environment  
pyenv local 3.5.3  
pip install --upgrade pip wheel  
pip install target-csv  
deactivate  

# run the tap

~/.virtualenvs/tap-bls/bin/tap-bls --config ~/tap-bls-config/config.json --catalog ~/tap-bls-config/catalog.json | ~/.virtualenvs/target-csv/bin/target-csv  

~/.virtualenvs/tap-bls/bin/tap-bls --config ~/tap-bls-config/config.json --catalog ~/tap-bls-config/catalog.json --state ~/tap-bls-config/state.json  | ~/.virtualenvs/target-csv/bin/target-csv

#### After you clone the directory, set Git up to remember your credentials (will be saved in ~/.git-credentials file.) - see https://www.shellhacks.com/git-config-username-password-store-credentials

# Pylint

pylint ~/tap-bls/tap_bls/ -d 'broad-except,chained-comparison,empty-docstring,fixme,invalid-name,line-too-long,missing-class-docstring,missing-function-docstring,missing-module-docstring,no-else-raise,no-else-return,too-few-public-methods,too-many-arguments,too-many-branches,too-many-lines,too-many-locals,ungrouped-imports,wrong-spelling-in-comment,wrong-spelling-in-docstring,too-many-return-statements,too-many-instance-attributes'
