git clone https://github.com/oltpbenchmark/oltpbench.git
sudo apt-get -y install ant
cd oltpbench
ant bootstrap
ant resolve
ant build
