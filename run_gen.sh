#!/usr/bin/env bash
SIMPLE=${1:-1}
MODERATE=${2:-1}
CHALLENGING=${3:-1}

python gen_subset.py --simple $SIMPLE --moderate $MODERATE --challenging $CHALLENGING --seed 1114


