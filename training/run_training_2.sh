#!/bin/bash

for i in `seq 0 200`; do
    # HYPERC_TEMPDIR=/tmp/hyperc/training/$1 HYPERC_USE_CACHE=1 HYPERC_STORE_STDOUT=1 HYPERC_STORE_SAS=1 HYPERC_SPLIT_OFF=1 HYPERC_SOLVER_MAX_TIME=6000 HYPERC_LOGLEVEL=info HYPERC_SOLVER_LOGLEVEL=info DOWNWARD_TOTAL_PUSHES=5000000000 HYPERC_STRICT_TYPING=1 python ./metaplanner.py training/$1/domain_${i}.pddl training/$1/problem_${i}.pddl
    python ./random_pddl_generator.py 1 3 ${i} ./training/$1/ &&
    HYPERC_TEMPDIR=/tmp/hyperc/training/$1 HYPERC_STORE_STDOUT=1 HYPERC_STORE_SAS=1 HYPERC_SPLIT_OFF=1 HYPERC_SOLVER_MAX_TIME=6000 HYPERC_LOGLEVEL=info HYPERC_SOLVER_LOGLEVEL=info DOWNWARD_TOTAL_PUSHES=5000000000 HYPERC_STRICT_TYPING=1 python ./metaplanner.py training/$1/domain_${i}.pddl training/$1/problem_${i}.pddl
done