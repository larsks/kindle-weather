#!/bin/sh

PAGES=/tmp/weather

cd $(dirname $0)

display=$(readlink "${PAGES}/display.png" 2> /dev/null || echo page1.png)
pagenum=${display%.png}
pagenum=${pagenum#page}

let pagenum++

display="page${pagenum}.png"
if [ -f "$PAGES/$display" ]; then
	ln -sf $display "$PAGES/display.png"
else
	ln -sf page1.png "$PAGES/display.png"
fi

sh display-weather.sh

