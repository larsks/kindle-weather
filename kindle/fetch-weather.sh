#!/bin/sh

BASEURL="http://weather.house"
PAGES="/tmp/weather"

cd $(dirname $0)

mkdir -p $PAGES
rm -f $PAGES/page*.png

i=1
while :; do
	curl -o $PAGES/page$i.png -sf \
		"${BASEURL}/page$i.png" || break

	let i++
done

