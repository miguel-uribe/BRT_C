#!/bin/bash
# We define the list of fleet sizes
fleets="150 200 250 300 350"
factor=10000
user=2.0
s="1 1 2 3"
popsize=101
mutprob=0.02
ntol=100
seed=2021
init = 001000100010001000100101011000111111101

for fleet in $fleets; do
    python optimizeFreqFrac_parent.py $factor $fleet $user $s $popsize $mutprob $ntol $seed $init
    # after the script is finished we get the best results
    init=`python getBestResult.py $factor $fleet $user $s $popsize $mutprob $ntol $seed $init`
done