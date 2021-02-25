REPOPATH=/home/azureuser/ostune

sudo apt-get update
#sudo apt-get -y install fabric
sudo rm /usr/bin/python
sudo ln -s /usr/bin/python3.6 /usr/bin/python
# Install Ubuntu packages

echo -e "\n--- Installing Ubuntu packages ---\n"
apt-get -qq update
apt-get -y install python3-pip python-dev python-mysqldb rabbitmq-server gradle default-jdk libmysqlclient-dev python3-tk

echo -e "\n--- Installing Python packages ---\n"
pip3 install --upgrade pip
pip install -r ${REPOPATH}/client/requirements.txt

