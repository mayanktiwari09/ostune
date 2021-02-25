REPOPATH=/home/azureuser/ostune

sudo apt-get update
#sudo apt-get -y install fabric
sudo rm /usr/bin/python
sudo ln -s /usr/bin/python3.6 /usr/bin/python
# Install Ubuntu packages

echo -e "\n--- Installing Ubuntu packages ---\n"
sudo apt-get -qq update
sudo apt-get -y install python3-pip python-dev python-mysqldb rabbitmq-server gradle default-jdk libmysqlclient-dev python3-tk

echo -e "\n--- Installing Python packages ---\n"
sudo pip3 install --upgrade pip
sudo pip install -r ${REPOPATH}/client/requirements.txt

