from metaplanner.planner import *
from metaplanner.pddl import parse_pddl_text

EQ_DOMAIN = """
(define (domain apples1)
    (:requirements :strips :typing :equality :negative-preconditions :disjunctive-preconditions)
    (:types ome otree ohand oapple ohome - object)
    (:predicates 
        (apple-is-on ?apple-0 - oapple ?tree-1 - otree)
        (hand-has ?hand-0 - ohand ?apple-1 - oapple)
        (is-at ?me-0 - ome ?tree-1 - otree)
    )
    (:action take-apple 
        :parameters (?apple-0 - oapple ?tree-1 - otree ?me-2 - ome ?hand - ohand)
        :precondition (and
            (apple-is-on ?apple-0 ?tree-1)
            (is-at ?me-2 ?tree-1)
            (= ?tree-1 tree)
        )
        :effect (and
            (hand-has ?hand ?apple-0)
            (not (is-at ?me-2 ?tree-1))
        )
    )

    (:action move-to-tree
        :parameters (?me-1 - ome ?tree-1 - otree ?home - ohome)
        :precondition (and
            (is-at ?me-1 ?home)
        )
        :effect (and
            (is-at ?me-1 ?tree-1)
        )
    )
)
"""

EQ_PROBLEM = """
(define (problem apples1)
    (:domain apples1)
    (:objects 
        me - ome apple - oapple hand - ohand tree - otree home - ohome
    )
    (:init
        (apple-is-on apple tree)
        (is-at me home)
    )
    (:goal
        (and
            (hand-has hand apple)
            (is-at me tree)
        )
    )
)
"""

def test_match_eq():
    # domain, problem, predicate_factory, object_factory, parameter_factories, action_factory \
    domain, problem, predicate_factory, object_factory, parameter_factories, action_factory \
        = parse_pddl_text(EQ_DOMAIN, EQ_PROBLEM)
    problem.prepare()
    action: Action = action_factory.get("take-apple")
    eq_pre = next(filter(lambda x: x.name == EQ_PREDICATE, action.precondition))
    is_at_pre = next(filter(lambda x: x.name == predicate_factory.get("is-at"), action.precondition)) 
    is_at_fact = next(filter(lambda x: x.name == predicate_factory.get("is-at"), problem.init)) 
    action.match_precondition(is_at_pre, is_at_fact)
    action.match_eq_precondition(eq_pre)

    
