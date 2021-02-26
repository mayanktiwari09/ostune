REPOPATH=/home/azureuser/ostune

#sudo apt-get -y install fabric
sudo rm /usr/bin/python
sudo ln -s /usr/bin/python3.6 /usr/bin/python

sudo apt-get -qq update

echo -e "\n--- Installing Ubuntu packages ---\n"
sudo apt-get -qq update
sudo apt-get -y install python3-pip python-dev default-jdk python3-tk

echo -e "\n--- Installing Python packages ---\n"
sudo pip3 install --upgrade pip
sudo pip install -r ${REPOPATH}/server/requirements.txt
