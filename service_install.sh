#!/bin/sh
echo "Installing Service..."
cp -f ./service/excbot.sh /usr/local/bin/
cp -f ./service/excbot.service /etc/systemd/system/excbot.service
sudo chmod a+x /usr/local/bin/excbot.sh
echo "Done!"
sudo systemctl daemon-reload
sudo systemctl enable excbot
echo "Starting service!"
sudo systemctl start excbot
sudo systemctl status excbot.service
