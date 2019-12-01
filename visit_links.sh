#!/usr/bin/env bash

while read ul; do
  chromium $ul
done < unsub_links.txt
