#!/bin/bash

fast-downward --plan-file ./out.plan --sas-file ./output.sas $1 $2 --translate-options --total-queue-pushes 50000000000 --search-options --evaluator 'hff=ff()' --evaluator 'hlm=lmcount(lm_rhw(reasonable_orders=true),transform=no_transform())' --search "lazy(alt([single(hff),single(hff,pref_only=true),single(hlm),single(hlm,pref_only=true),type_based([hff,g()])],boost=1000), preferred=[hff,hlm], cost_type=one, reopen_closed=false, randomize_successors=true, preferred_successors_first=false, bound=infinity)"