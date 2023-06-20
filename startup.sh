# Perform a quick update on your instance:
sudo yum update -y
sudo yum install git -y
sudp yum install python3-pip -y

pip3 install python-dotenv
pip3 install bs4
pip3 install html5lib

# Clone, enter, and pull the repository
[ ! -d "~/site-watcher" ] && git clone https://github.com/zawie/site-watcher.git ~/site-watcher
cd site-watcher
git pull 

nohup python3 main.py &



