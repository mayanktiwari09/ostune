#!/bin/bash

fab run_oltpbench > loop_output.txt
resultStr=$(cat loop_output.txt | grep "Results")
echo $resultStr > loop_output.txt
