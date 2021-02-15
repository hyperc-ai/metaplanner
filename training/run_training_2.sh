#!/bin/bash

for i in `seq 0 200`; do
    python ./training/random_pddl_generator.py 1 3 ${i} ./training/$1/ &&
    HYPERC_TEMPDIR=/var/data/userdata/training/$1 HYPERC_STORE_STDOUT=1 HYPERC_STORE_SAS=1 HYPERC_SPLIT_OFF=1 HYPERC_SOLVER_MAX_TIME=6000 HYPERC_LOGLEVEL=info HYPERC_SOLVER_LOGLEVEL=info DOWNWARD_TOTAL_PUSHES=5000000000 HYPERC_STRICT_TYPING=1 python -m metaplanner training/$1/domain_${i}.pddl training/$1/problem_${i}.pddl training/$1/out$i.mplan training/$1/out$i.plan || exit -1
    WORKDIR=$(ls -td /var/data/userdata/training/$1/* | head -1)
    cp ./training/$1/out$i.plan $WORKDIR/fd.plan
    cp ./training/$1/domain_${i}.pddl $WORKDIR/domain_m0.pddl
    cp ./training/$1/problem_${i}.pddl $WORKDIR/pblem_m0.pddl
done
