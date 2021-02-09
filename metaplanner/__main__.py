import sys
# sys.path.append(".")
# import gc
# gc.disable()
from metaplanner.planner import Predicate, Action, Problem, Domain, Object, PredicateId, Parameter
import metaplanner.pddl
from hyperc import solve

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
