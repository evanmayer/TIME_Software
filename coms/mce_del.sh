#!/bin/bash
#mce = $1
ssh -T time@time-mce-$1 'rm /data/cryo/current_data/temp*'
