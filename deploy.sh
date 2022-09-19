#!/usr/bin/env bash

systemctl stop klumba_deal_feed_bot
rm -f  /etc/systemd/system/klumba_deal_feed_bot.service
cp -f ./klumba_deal_feed_bot.service /etc/systemd/system/
systemctl start klumba_deal_feed_bot
systemctl enable klumba_deal_feed_bot
systemctl daemon-reload