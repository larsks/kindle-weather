#!/bin/sh

/etc/init.d/framework stop
/etc/init.d/powerd stop
/mnt/us/weather/button-server.sh &
/mnt/us/weather/fetch-and-display-weather.sh
