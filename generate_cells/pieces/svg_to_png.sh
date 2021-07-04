#!/bin/bash

for i in `find . -name "*.svg" -type f`; do
	inkscape -w 200 -h 200 $i -o ${i%.*}.png
	echo ${i%.*}
done

