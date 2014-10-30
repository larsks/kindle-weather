#!/bin/sh

cd $(dirname $0)

exec python buttons.py \
	-e 1 194 1 "./next-page.sh" \
	/dev/input/event1

