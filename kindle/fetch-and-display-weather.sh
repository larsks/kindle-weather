#!/bin/sh

cd $(dirname $0)

./fetch-weather.sh
./display-weather.sh

