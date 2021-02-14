import sys
import os
# sys.path.append(".")
# import gc
# gc.disable()
import metaplanner.planner
from metaplanner.planner import Predicate, Action, Problem, Domain, Object, PredicateId, Parameter
import metaplanner.pddl
import metaplanner.plan2metaplan
from hyperc import solve
import hyperc
import metaplanner.hints

hyperc.settings.STORE_STDOUT=1 
hyperc.settings.STORE_SAS=1 
hyperc.settings.HYPERC_SPLIT_OFF=1 
hyperc.settings.HYPERC_SOLVER_MAX_TIME=6000 
hyperc.settings.HYPERC_LOGLEVEL=os.getenv("HYPERC_LOGLEVEL", "info")
hyperc.settings.HYPERC_SOLVER_LOGLEVEL="info" 
hyperc.settings.DOWNWARD_TOTAL_PUSHES=5000000000 
hyperc.settings.HYPERC_STRICT_TYPING=1 
hyperc.settings.HYPERC_LIN_COUNT=int(os.getenv("HYPERC_LIN_COUNT", 10))
hyperc.settings.HYPERC_NEW_OBJECTS=int(os.getenv("HYPERC_NEW_OBJECTS", 7))
hyperc.settings.HYPERC_ASE_OFF=1

if __name__ == "__main__":
    DOM = open(sys.argv[1]).read()
    PROB = open(sys.argv[2]).read()
    domain, problem, predicate_factory, object_factory, parameter_factories, action_factory = \
        metaplanner.pddl.parse_pddl_text(DOM, PROB)
    problem.prepare()
    metadata = {}
    if len(sys.argv) >= 5:  # solution to problem for "hinted run"
        s_plan = open(sys.argv[4]).read()
        pre_hints, eff_hints = metaplanner.plan2metaplan.load_hints(s_plan, action_factory=action_factory,
                parameter_factories=parameter_factories, object_factory=object_factory)
        metaplanner.hints.pre_hints = pre_hints
        metaplanner.hints.eff_hints = eff_hints

    solve(problem.match_goal, metadata=metadata)

    metaplanner.pddl.dump_task(domain, problem, action_factory)

    print("Plan:")
    # while step.item:
        # print(f"({action_factory.to_name(step.item)} ...)")
        # step = step.next
    plan = problem._tracer.str_plan()
    print(plan)
    if len(sys.argv) >= 4:
        open(sys.argv[3], "w+").write(plan)
    open(metadata["work_dir"]+"/meta0.plan", "w+").write(plan)
    open(metadata["work_dir"]+"/meta0.domain", "w+").write(DOM)
    open(metadata["work_dir"]+"/meta0.problem", "w+").write(PROB)

