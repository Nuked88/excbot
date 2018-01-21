#!/bin/sh
echo "Installing Service..."
cp ./service/excbot.sh /usr/local/bin/
cp ./service/excbot.service /etc/systemd/system/excbot.service
echo "Done!"
sudo systemctl daemon reload
sudo systemctl enable excbot
echo "Starting service!"
sudo systemctl start excbot
