#!/bin/bash

mkdir -p ./training/$1
mkdir -p /var/data/userdata/training/$1
rm ./training/$1/*
for i in `seq 0 2000`; do
    python ./training/random_pddl_generator.py 1 6 ${i} ./training/$1/ 10
    [ $? -eq 0 ] && echo "pddl generation success" || exit 1
    if [ `wc -w ./training/$1/out$i.plan` -gt 19 ]; then
        if [ `wc -w ./training/$1/out$i.plan` -gt 25 ]; then
            HYPERC_TEMPDIR=/var/data/userdata/training/$1 HYPERC_STORE_STDOUT=1 HYPERC_STORE_SAS=1 HYPERC_SPLIT_OFF=1 HYPERC_SOLVER_MAX_TIME=6000 HYPERC_LOGLEVEL=info HYPERC_SOLVER_LOGLEVEL=info DOWNWARD_TOTAL_PUSHES=5000000000 HYPERC_STRICT_TYPING=1 HYPERC_LIN_COUNT=30 HYPERC_NEW_OBJECTS=25 python -m metaplanner training/$1/domain_${i}.pddl training/$1/problem_${i}.pddl training/$1/out$i.mplan training/$1/out$i.plan
        else
            HYPERC_TEMPDIR=/var/data/userdata/training/$1 HYPERC_STORE_STDOUT=1 HYPERC_STORE_SAS=1 HYPERC_SPLIT_OFF=1 HYPERC_SOLVER_MAX_TIME=6000 HYPERC_LOGLEVEL=info HYPERC_SOLVER_LOGLEVEL=info DOWNWARD_TOTAL_PUSHES=5000000000 HYPERC_STRICT_TYPING=1 HYPERC_LIN_COUNT=20 HYPERC_NEW_OBJECTS=15 python -m metaplanner training/$1/domain_${i}.pddl training/$1/problem_${i}.pddl training/$1/out$i.mplan training/$1/out$i.plan
    fi
    else
        HYPERC_TEMPDIR=/var/data/userdata/training/$1 HYPERC_STORE_STDOUT=1 HYPERC_STORE_SAS=1 HYPERC_SPLIT_OFF=1 HYPERC_SOLVER_MAX_TIME=6000 HYPERC_LOGLEVEL=info HYPERC_SOLVER_LOGLEVEL=info DOWNWARD_TOTAL_PUSHES=5000000000 HYPERC_STRICT_TYPING=1 HYPERC_LIN_COUNT=15 HYPERC_NEW_OBJECTS=10 python -m metaplanner training/$1/domain_${i}.pddl training/$1/problem_${i}.pddl training/$1/out$i.mplan training/$1/out$i.plan
    fi
    MPEXIT=$?
    WORKDIR=$(ls -td /var/data/userdata/training/$1/* | head -1)
    cp ./training/$1/out$i.plan $WORKDIR/fd.plan
    cp ./training/$1/domain_${i}.pddl $WORKDIR/domain_m0.pddl
    cp ./training/$1/problem_${i}.pddl $WORKDIR/problem_m0.pddl
    # [ $MPEXIT -eq 0 ] && echo "hinted solve success" || exit 1
done
