import sys
# sys.path.append(".")
# import gc
# gc.disable()
from metaplanner.planner import Predicate, Action, Problem, Domain, Object, PredicateId, Parameter
import metaplanner.pddl
from hyperc import solve
import hyperc
hyperc.settings.STORE_STDOUT=1 
hyperc.settings.STORE_SAS=1 
hyperc.settings.HYPERC_SPLIT_OFF=1 
hyperc.settings.HYPERC_SOLVER_MAX_TIME=6000 
hyperc.settings.HYPERC_LOGLEVEL="info" 
hyperc.settings.HYPERC_SOLVER_LOGLEVEL="info" 
hyperc.settings.DOWNWARD_TOTAL_PUSHES=5000000000 
hyperc.settings.HYPERC_STRICT_TYPING=1 
hyperc.settings.HYPERC_LIN_COUNT=9 
hyperc.settings.HYPERC_NEW_OBJECTS=7 
hyperc.settings.HYPERC_ASE_OFF=1

if __name__ == "__main__":
    domain, problem, predicate_factory, object_factory, parameter_factories, action_factory = \
        metaplanner.pddl.parse_pddl_text(open(sys.argv[1]).read(), open(sys.argv[2]).read())
    problem.prepare()
    solve(problem.match_goal)

    metaplanner.pddl.dump_task(domain, problem, action_factory)

    print("Plan:")
    step = problem.plan.head
    while step.item:
        print(f"({action_factory.to_name(step.item)} ...)")
        step = step.next
