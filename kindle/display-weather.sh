#!/bin/sh

PAGES=/tmp/weather

cd $(dirname $0)

eips -c
eips -c

if ! [ -f "${PAGES}/page1.png" ]; then
	eips -g weather-image-error.png
	exit
fi

display=$(readlink "${PAGES}/display.png" 2> /dev/null || echo page1.png)
eips -g "$PAGES/$display"

