#!/bin/bash

sysctl vm.swappiness > vm_smapiness.txt
sysctl vm.dirty_background_ratio > vm_dirty_background_ratio.txt
sysctl vm.dirty_ratio > vm_dirty_ratio.txt
sysctl vm.overcommit_ratio > vm_overcommit_ratio.txt
