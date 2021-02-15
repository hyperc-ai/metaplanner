from metaplanner.planner import *
from metaplanner.pddl import parse_pddl_text
import metaplanner.pddl
import metaplanner.plan2metaplan
import metaplanner.hints

metaplanner.pddl.DEBUG = 1

DOMAIN = """
(define (domain random)
    (:requirements :strips :typing :equality :negative-preconditions :disjunctive-preconditions)
    (:types rpclass1 rpclass2 - object)
    (:predicates 
        (rppred1 ?v1 - rpclass2 ?v2 - rpclass1)
        (rppred2 ?v1 - rpclass1 ?v2 - rpclass1)
        (rppred3 ?v1 - rpclass1 ?v2 - rpclass2)
        (rppred4 ?v1 - rpclass2 ?v2 - rpclass1)
    )
        
    
        (:action random-action-268617
            :parameters (?rpclass2-1 - rpclass2 ?rpclass1-0 - rpclass1 ?rpclass1-2 - rpclass1)
            :precondition (and
                (rppred2 rpobj2 rpobj2)
            )
            :effect (and
                (rppred3 ?rpclass1-2 ?rpclass2-1)
                (rppred4 rpobj4 ?rpclass1-0)
            )
        )
        
    
        (:action random-action-251873
            :parameters (?rpclass2-2 - rpclass2 ?rpclass2-1 - rpclass2 ?rpclass1-4 - rpclass1 ?rpclass1-3 - rpclass1)
            :precondition (and
                (rppred4 rpobj4 ?rpclass1-4)
                (rppred4 rpobj3 ?rpclass1-3)
                (rppred4 ?rpclass2-2 ?rpclass1-4)
            )
            :effect (and
                (rppred1 ?rpclass2-1 ?rpclass1-4)
            )
        )
        
)
    
"""

PROBLEM = """
(define (problem random)
    (:domain random)
    (:objects 
        rpobj1 rpobj2 - rpclass1 rpobj3 rpobj4 - rpclass2
    )
    (:init
        (rppred4 rpobj3 rpobj1)
        (rppred2 rpobj2 rpobj2)
        (rppred1 rpobj3 rpobj2)
        (rppred2 rpobj1 rpobj1)
    )
    (:goal
        (and
            (rppred1 rpobj4 rpobj2)
        )
    )
)
"""

PLAN = """
(random-action-268617 rpobj4 rpobj2 rpobj2)
(random-action-251873 rpobj4 rpobj4 rpobj2 rpobj1)
; cost = 2 (unit cost)
"""



def test_load_hints_assert():
    domain, problem, predicate_factory, object_factory, parameter_factories, action_factory \
        = parse_pddl_text(DOMAIN, PROBLEM)
    problem.prepare()
    pre_hints, eff_hints = metaplanner.plan2metaplan.load_hints(PLAN, action_factory=action_factory, 
            parameter_factories=parameter_factories, object_factory=object_factory)
