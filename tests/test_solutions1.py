from metaplanner.planner import *
from metaplanner.pddl import parse_pddl_text
import metaplanner.pddl

metaplanner.pddl.DEBUG = 1

DOMAIN = """
(define (domain random)
    (:requirements :strips :typing :equality :negative-preconditions :disjunctive-preconditions)
    (:types rpclass1 rpclass2 rpclass3 rpclass4 - object)
    (:predicates 
        (rppred1 ?v1 - rpclass1 ?v2 - rpclass1)
        (rppred2 ?v1 - rpclass1 ?v2 - rpclass1)
        (rppred3 ?v1 - rpclass2 ?v2 - rpclass3)
        (rppred4 ?v1 - rpclass2 ?v2 - rpclass4)
    )
    
        (:action random-action-208713
            :parameters (?rpclass2-5 - rpclass2 ?rpclass4-7 - rpclass4 ?rpclass1-3 - rpclass1 ?rpclass1-6 - rpclass1)
            :precondition (and
                (rppred2 ?rpclass1-3 ?rpclass1-6)
            )
            :effect (and
                (rppred4 ?rpclass2-5 ?rpclass4-7)
            )
        )
        
)
"""

PROBLEM = """
(define (problem random)
    (:domain random)
    (:objects 
        rpobj1 rpobj2 rpobj3 rpobj4 - rpclass1 rpobj5 rpobj6 - rpclass2 rpobj7 rpobj8 rpobj9 rpobj10 - rpclass3 rpobj11 rpobj12 rpobj13 rpobj14 - rpclass4
    )
    (:init
        (rppred1 rpobj2 rpobj3)
        (rppred1 rpobj3 rpobj4)
        (rppred3 rpobj5 rpobj7)
        (rppred3 rpobj6 rpobj8)
        (rppred2 rpobj3 rpobj2)
    )
    (:goal
        (and
            (rppred4 rpobj5 rpobj14)
            (rppred4 rpobj5 rpobj13)
        )
    )
)
"""

PLAN = """
(random-action-208713 rpobj5 rpobj14 rpobj3 rpobj2)
(random-action-208713 rpobj5 rpobj13 rpobj3 rpobj2)
; cost = 2 (unit cost)
"""

def test_action_freevar():
    domain, problem, predicate_factory, object_factory, parameter_factories, action_factory \
        = parse_pddl_text(DOMAIN, PROBLEM)
    action: Action = action_factory.get("random-action-208713")
    # match 2 preconditions
    pre1 = next(filter(lambda x: x.name == predicate_factory.get("rppred2"), action.precondition))

    fact1 = next(filter(lambda x: x.name == predicate_factory.get("rppred2"), problem.init)) 
    action.match_precondition(pre1, fact1)

    # run effect
    eff1 = next(filter(
        lambda x: x.name == predicate_factory.get("rppred4")
            and x.negated == False, action.effect)) 
    obj1 = object_factory.objects["rpobj5"]
    obj2 = object_factory.objects["rpobj14"]
    action.run_effect(eff1, obj1, obj2, None)

    # clean preconditions
    action.clean_precondition(pre1)
    # clean effect 
    action.clean_effect(eff1)

    # SECOND
    action.match_precondition(pre1, fact1)
    obj1 = object_factory.objects["rpobj5"]
    obj2 = object_factory.objects["rpobj13"]
    action.run_effect(eff1, obj1, obj2, None)


    f1 = next(filter(lambda x: x.name == predicate_factory.get("rppred4") and \
            x.obj_2 == object_factory.get("rpobj14"), problem.init)) 
    g1 = next(filter(lambda x: x.name == predicate_factory.get("rppred4") and \
            x.obj_2 == object_factory.get("rpobj14"), problem.goal)) 
    f2 = next(filter(lambda x: x.name == predicate_factory.get("rppred4") and \
            x.obj_2 == object_factory.get("rpobj13"), problem.init)) 
    g2 = next(filter(lambda x: x.name == predicate_factory.get("rppred4") and \
            x.obj_2 == object_factory.get("rpobj13"), problem.goal)) 
    problem.match_goal_condition(f1, g1)
    problem.match_goal_condition(f2, g2)
    problem.match_goal()

    print(problem._tracer.str_plan())