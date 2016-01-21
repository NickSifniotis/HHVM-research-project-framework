#!/bin/bash

sources_root="./Sources"
results_root="./results"
test_version=("wordpress" "drupal7" "mediawiki")


# create the results subdirectories.
# nuke any existing results (make sure they have been saved
# or processed before executing this script)
rm -r $results_root
mkdir $results_root
for hhvm_var in "$@"
do
   mkdir $results_root/$hhvm_var
done


# run the benchmarking tests on the hhvm builds

for hhvm_var in "$@"
do
   for i in `seq 1 20`
   do
      for test in "${test_version[@]}"
      do
         echo "$hhvm_var: Test $i $test"
         hhvm ~/git/oss-performance/perf.php --$test --hhvm=$sources_root/$hhvm_var 2> /dev/null > $results_root/$hhvm_var/$test-$i.txt
      done
   done
done
