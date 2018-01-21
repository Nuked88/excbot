#!/bin/sh
echo "Installing Service..."
mv ./service/excbot.sh /usr/local/bin/
mv ./service/excbot.service /etc/systemd/system/excbot.service
echo "Done!"
sudo systemctl daemon reload
sudo systemctl enable excbot
echo "Starting service!"
sudo systemctl start excbot
