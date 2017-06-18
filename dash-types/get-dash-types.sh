#!/bin/bash

dhtypes_url='https://raw.githubusercontent.com/Kapeli/Dash-iOS/master/Dash/DHTypes.m'
[[ ! -a DHTypes.m ]] && curl "$dhtypes_url" > DHTypes.m
# curl https://raw.githubusercontent.com/Kapeli/Dash-iOS/master/Dash/DHTypes.m > DHTypes.m

# get types
cat DHTypes.m |
    grep 'orderedTypeObjects addObject' |
    sed 's/^.*typeWithHumanType:@"//' |
    sed 's/".*//' |
    sort > types

# get aliasas
cat DHTypes.m |
    grep 'orderedTypeObjects addObject' |
    sed 's/^.*typeWithHumanType:@"//' |
    grep 'aliases:@' |
    sed 's/".*aliases:@/|/' |
    sed 's/]];//' |
    sed 's/@//g' > aliases

