from metaplanner.planner import *
from metaplanner.pddl import parse_pddl_text
import metaplanner.pddl
import pytest

metaplanner.pddl.DEBUG = 1

DOMAIN = """
(define (domain random)
    (:requirements :strips :typing :equality :negative-preconditions :disjunctive-preconditions)
    (:types rpclass1 rpclass2 - object)
    (:predicates 
        (rppred1 ?v1 - rpclass2 ?v2 - rpclass2)
        (rppred2 ?v1 - rpclass2 ?v2 - rpclass2)
        (rppred3 ?v1 - rpclass2 ?v2 - rpclass1)
        (rppred4 ?v1 - rpclass1 ?v2 - rpclass1)
    )
        
        (:action random-action-503217
            :parameters (?rpclass2-0 - rpclass2 ?rpclass1-2 - rpclass1 ?rpclass1-1 - rpclass1 ?rpclass2-3 - rpclass2)
            :precondition (and
                (rppred2 ?rpclass2-3 ?rpclass2-0)
            )
            :effect (and
                (rppred4 ?rpclass1-2 ?rpclass1-1)
                (not (rppred4 ?rpclass1-2 rpobj2))
            )
        )
)
"""

PROBLEM = """
(define (problem random)
    (:domain random)
    (:objects 
        rpobj1 rpobj2 rpobj3 - rpclass1 rpobj4 - rpclass2
    )
    (:init
        (rppred3 rpobj4 rpobj1)
        (rppred2 rpobj4 rpobj4)
        (rppred4 rpobj3 rpobj3)
        (rppred1 rpobj4 rpobj4)
    )
    (:goal
        (and
            (rppred4 rpobj3 rpobj2)
            (rppred4 rpobj1 rpobj2)
        )
    )
)
"""

PLAN = """
(random-action-503217 rpobj4 rpobj1 rpobj2 rpobj4)
(random-action-503217 rpobj4 rpobj3 rpobj2 rpobj4)
; cost = 2 (unit cost)
"""

@pytest.mark.skip(reason="Memory overflow at translation")
def test_action_remove_nonexisting_fact():
    """Check if we can remove non-existing fact.
    This situation is not supported by HyperC metaplanner,
    But is expected behaviour of classic solvers
    """
    domain, problem, predicate_factory, object_factory, parameter_factories, action_factory \
        = parse_pddl_text(DOMAIN, PROBLEM)
    
    # TODO HERE:
    # - [x] create ticket to fix set.remove behaviour to disallow removal if x is not in set
    # - [ ] add the check to run_effect to only remove the element if it is in list
    # - [ ] 

    action: Action = action_factory.get("random-action-503217")
    # match 2 preconditions
    pre1 = next(filter(lambda x: x.name == predicate_factory.get("rppred2"), action.precondition))

    fact1 = next(filter(lambda x: x.name == predicate_factory.get("rppred2"), problem.init)) 

    action.match_precondition(pre1, fact1)

    # run effect
    eff1 = next(filter(
        lambda x: x.name == predicate_factory.get("rppred4")
            and x.negated == False, action.effect)) 
    eff2 = next(filter(
        lambda x: x.name == predicate_factory.get("rppred4")
            and x.negated == True, action.effect)) 
    obj1 = object_factory.objects["rpobj1"]
    obj2 = object_factory.objects["rpobj2"]
    fact_remove = next(filter(lambda x: x.name == predicate_factory.get("rppred4") and
                                    x.obj_2 == object_factory.get("rpobj2"), problem.init)) 
    action.run_effect(eff2, obj1, None, fact_remove)
    action.run_effect(eff1, obj1, obj2, None)


    # clean preconditions
    action.clean_precondition(pre1)
    # clean effect 
    action.clean_effect(eff1)
    action.clean_effect(eff2)

    # SECOND

    fact2 = next(filter(lambda x: x.name == predicate_factory.get("rppred2") and\
           x.obj_1 == object_factory.get("rpobj4") , problem.init)) 
    action.match_precondition(pre1, fact2)

    # run effect
    eff1 = next(filter(
        lambda x: x.name == predicate_factory.get("rppred4")
            and x.negated == False, action.effect)) 
    eff2 = next(filter(
        lambda x: x.name == predicate_factory.get("rppred4")
            and x.negated == True, action.effect)) 
    obj1 = object_factory.objects["rpobj3"]
    obj2 = object_factory.objects["rpobj2"]
    fact_remove = next(filter(lambda x: x.name == predicate_factory.get("rppred4") and
                                    x.obj_2 == object_factory.get("rpobj2"), problem.init)) 
    action.run_effect(eff2, obj1, None, fact_remove)
    action.run_effect(eff1, obj1, obj2, None)


    f1 = next(filter(lambda x: x.name == predicate_factory.get("rppred4") and \
            x.obj_1 == object_factory.get("rpobj3") and 
            x.obj_2 == object_factory.get("rpobj2"), problem.init)) 
    g1 = next(filter(lambda x: x.name == predicate_factory.get("rppred4") and \
            x.obj_1 == object_factory.get("rpobj3") and 
            x.obj_2 == object_factory.get("rpobj2"), problem.goal)) 
    problem.match_goal_condition(f1, g1)


    f2 = next(filter(lambda x: x.name == predicate_factory.get("rppred4") and \
            x.obj_1 == object_factory.get("rpobj1") and 
            x.obj_2 == object_factory.get("rpobj2"), problem.init)) 
    g2 = next(filter(lambda x: x.name == predicate_factory.get("rppred4") and \
            x.obj_1 == object_factory.get("rpobj1") and 
            x.obj_2 == object_factory.get("rpobj2"), problem.goal)) 
    problem.match_goal_condition(f2, g2)



    problem.match_goal()