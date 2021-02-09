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

NEQ_DOMAIN = """
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
            (not (= ?tree-1 tree))
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
    is_at_fact = next(filter(lambda x: x.name == predicate_factory.get("is-at"), problem.goal)) 
    # move goal fact to init
    problem.init.add(is_at_fact)
    print("WILL BE MATCHING", eq_pre.par_1.obj, eq_pre.par_2.obj)
    action.match_precondition(is_at_pre, is_at_fact)
    print("WILL BE MATCHING 2", eq_pre.par_1.obj, eq_pre.par_2.obj)
    action.match_eq_precondition(eq_pre)


def test_not_match_eq():
    # domain, problem, predicate_factory, object_factory, parameter_factories, action_factory \
    domain, problem, predicate_factory, object_factory, parameter_factories, action_factory \
        = parse_pddl_text(NEQ_DOMAIN, EQ_PROBLEM)
    problem.prepare()
    action: Action = action_factory.get("take-apple")
    eq_pre = next(filter(lambda x: x.name == EQ_PREDICATE, action.precondition))
    is_at_pre = next(filter(lambda x: x.name == predicate_factory.get("is-at"), action.precondition)) 
    is_at_fact = next(filter(lambda x: x.name == predicate_factory.get("is-at"), problem.init)) 
    # move goal fact to init
    problem.init.add(is_at_fact)
    print("WILL BE MATCHING", eq_pre.par_1.obj, eq_pre.par_2.obj)
    action.match_precondition(is_at_pre, is_at_fact)
    print("WILL BE MATCHING 2", eq_pre.par_1.obj, eq_pre.par_2.obj)
    action.match_eq_precondition(eq_pre)

MAZE_DOMAIN = """
(define (domain maze1)
    (:requirements :strips :typing :equality :negative-preconditions :disjunctive-preconditions)
    (:types agent node - object)
    (:predicates 
        (is-at ?v1 - agent ?v2 - node)
        (node-connected ?n1 - node ?n2 - node)
    )

    (:action move-to-next-node
        :parameters (?agent - agent ?node-1 - node ?node-2 - node)
        :precondition (and
            (is-at ?agent ?node-1)
            (node-connected ?node-1 ?node-2)
        )
        :effect (and
            (not (is-at ?agent ?node-1))
            (is-at ?agent ?node-2)
        )
    )
)
"""

MAZE_PROBLEM = """
(define (problem maze1)
    (:domain maze1)
    (:objects 
        agent - agent n1 n2 n3 n4 - node
    )
    (:init
        (is-at agent n2)
        (node-connected n1 n2)
        (node-connected n2 n3)
        (node-connected n3 n4)
    )
    (:goal
        (and
            (is-at agent n4)
        )
    )
)
"""

def test_action_twice():
    domain, problem, predicate_factory, object_factory, parameter_factories, action_factory \
        = parse_pddl_text(MAZE_DOMAIN, MAZE_PROBLEM)
    action: Action = action_factory.get("move-to-next-node")
    # match 2 preconditions
    node_connected_pre = next(filter(lambda x: x.name == predicate_factory.get("node-connected"), action.precondition))
    is_at_pre = next(filter(lambda x: x.name == predicate_factory.get("is-at"), action.precondition)) 

    is_at_fact = next(filter(lambda x: x.name == predicate_factory.get("is-at"), problem.init)) 
    action.match_precondition(is_at_pre, is_at_fact)

    node_connected_fact = next(filter(
        lambda x: x.name == predicate_factory.get("node-connected") \
            and x.par_1.obj == object_factory.get("n2"), problem.init)) 
    action.match_precondition(node_connected_pre, node_connected_fact)

    # run effect
    is_at_eff = next(filter(
        lambda x: x.name == predicate_factory.get("is-at")
            and x.negated == False, action.effect)) 
    is_at_eff_neg = next(filter(
        lambda x: x.name == predicate_factory.get("is-at")
            and x.negated == True, action.effect)) 
    action.run_effect(is_at_eff_neg, None, None, is_at_fact)
    action.run_effect(is_at_eff, None, None, None)

    # clean parameters
    action.clean_parameter(node_connected_pre.par_1)
    action.clean_parameter(node_connected_pre.par_2)
    action.clean_parameter(is_at_pre.par_1)
    action.clean_parameter(is_at_pre.par_2)

    # clean preconditions
    action.clean_precondition(node_connected_pre)
    action.clean_precondition(is_at_pre)
    # clean effect 
    action.clean_effect(is_at_eff)
    action.clean_effect(is_at_eff_neg)

    # SECOND

    is_at_fact = next(filter(lambda x: x.name == predicate_factory.get("is-at"), problem.init)) 
    action.match_precondition(is_at_pre, is_at_fact)
    node_connected_fact = next(filter(
        lambda x: x.name == predicate_factory.get("node-connected") \
            and x.par_1.obj == object_factory.get("n3"), problem.init)) 
    action.match_precondition(node_connected_pre, node_connected_fact)

    # run effect
    is_at_eff = next(filter(
        lambda x: x.name == predicate_factory.get("is-at")
            and x.negated == False, action.effect)) 
    is_at_eff_neg = next(filter(
        lambda x: x.name == predicate_factory.get("is-at")
            and x.negated == True, action.effect)) 
    action.run_effect(is_at_eff_neg, None, None, is_at_fact)
    action.run_effect(is_at_eff, None, None, None)


    # clean parameters
    action.clean_parameter(node_connected_pre.par_1)
    action.clean_parameter(node_connected_pre.par_2)
    action.clean_parameter(is_at_pre.par_1)
    action.clean_parameter(is_at_pre.par_2)

    # clean preconditions
    action.clean_precondition(node_connected_pre)
    action.clean_precondition(is_at_pre)
    # clean effect 
    action.clean_effect(is_at_eff) 
    action.clean_effect(is_at_eff_neg)

    is_at_fact = next(filter(lambda x: x.name == predicate_factory.get("is-at"), problem.init)) 
    is_at_goal = next(filter(lambda x: x.name == predicate_factory.get("is-at"), problem.goal)) 
    problem.match_goal_condition(is_at_fact, is_at_goal)
    problem.match_goal()


def test_cant_execute_next_wo_cleaning():
    domain, problem, predicate_factory, object_factory, parameter_factories, action_factory \
        = parse_pddl_text(MAZE_DOMAIN, MAZE_PROBLEM)
    action: Action = action_factory.get("move-to-next-node")
    # match 2 preconditions
    node_connected_pre = next(filter(lambda x: x.name == predicate_factory.get("node-connected"), action.precondition))
    is_at_pre = next(filter(lambda x: x.name == predicate_factory.get("is-at"), action.precondition)) 

    is_at_fact = next(filter(lambda x: x.name == predicate_factory.get("is-at"), problem.init)) 
    action.match_precondition(is_at_pre, is_at_fact)

    node_connected_fact = next(filter(
        lambda x: x.name == predicate_factory.get("node-connected") \
            and x.par_1.obj == object_factory.get("n2"), problem.init)) 
    action.match_precondition(node_connected_pre, node_connected_fact)

    # run effect
    is_at_eff = next(filter(
        lambda x: x.name == predicate_factory.get("is-at")
            and x.negated == False, action.effect)) 
    is_at_eff_neg = next(filter(
        lambda x: x.name == predicate_factory.get("is-at")
            and x.negated == True, action.effect)) 
    action.run_effect(is_at_eff_neg, None, None, is_at_fact)
    action.run_effect(is_at_eff, None, None, None)

    # clean parameters
    # action.clean_parameter(node_connected_pre.par_1)
    action.clean_parameter(node_connected_pre.par_2)
    action.clean_parameter(is_at_pre.par_1)
    # action.clean_parameter(is_at_pre.par_2)

    # clean preconditions
    action.clean_precondition(node_connected_pre)
    action.clean_precondition(is_at_pre)
    # clean effect 
    action.clean_effect(is_at_eff)
    action.clean_effect(is_at_eff_neg)

    # SECOND

    is_at_fact = next(filter(lambda x: x.name == predicate_factory.get("is-at"), problem.init)) 
    try:
        action.match_precondition(is_at_pre, is_at_fact)
    except AssertionError:
        return
    raise AssertionError("Can't reach here")
    node_connected_fact = next(filter(
        lambda x: x.name == predicate_factory.get("node-connected") \
            and x.par_1.obj == object_factory.get("n3"), problem.init)) 
    action.match_precondition(node_connected_pre, node_connected_fact)

    # run effect
    is_at_eff = next(filter(
        lambda x: x.name == predicate_factory.get("is-at")
            and x.negated == False, action.effect)) 
    is_at_eff_neg = next(filter(
        lambda x: x.name == predicate_factory.get("is-at")
            and x.negated == True, action.effect)) 
    action.run_effect(is_at_eff_neg, None, None, is_at_fact)
    action.run_effect(is_at_eff, None, None, None)


    # clean parameters
    action.clean_parameter(node_connected_pre.par_1)
    action.clean_parameter(node_connected_pre.par_2)
    action.clean_parameter(is_at_pre.par_1)
    action.clean_parameter(is_at_pre.par_2)

    # clean preconditions
    action.clean_precondition(node_connected_pre)
    action.clean_precondition(is_at_pre)
    # clean effect 
    action.clean_effect(is_at_eff) 
    action.clean_effect(is_at_eff_neg)

    is_at_fact = next(filter(lambda x: x.name == predicate_factory.get("is-at"), problem.init)) 
    is_at_goal = next(filter(lambda x: x.name == predicate_factory.get("is-at"), problem.goal)) 
    problem.match_goal_condition(is_at_fact, is_at_goal)
    problem.match_goal()


def test_cant_clean_to_match():
    "test if planner can circumvent proper matching with spurious cleaning"
    domain, problem, predicate_factory, object_factory, parameter_factories, action_factory \
        = parse_pddl_text(MAZE_DOMAIN, MAZE_PROBLEM)
    action: Action = action_factory.get("move-to-next-node")
    # match 2 preconditions
    node_connected_pre = next(filter(lambda x: x.name == predicate_factory.get("node-connected"), action.precondition))
    is_at_pre = next(filter(lambda x: x.name == predicate_factory.get("is-at"), action.precondition)) 

    is_at_fact = next(filter(lambda x: x.name == predicate_factory.get("is-at"), problem.init)) 
    action.match_precondition(is_at_pre, is_at_fact)

    node_connected_fact_wrong = next(filter(
        lambda x: x.name == predicate_factory.get("node-connected") \
            and x.par_1.obj == object_factory.get("n3"), problem.init)) 
    try:
        action.clean_parameter(node_connected_pre.par_1)
        action.clean_parameter(node_connected_pre.par_2)
        action.match_precondition(node_connected_pre, node_connected_fact_wrong)

        # run effect
        is_at_eff = next(filter(
            lambda x: x.name == predicate_factory.get("is-at")
                and x.negated == False, action.effect)) 
        is_at_eff_neg = next(filter(
            lambda x: x.name == predicate_factory.get("is-at")
                and x.negated == True, action.effect)) 
        action.run_effect(is_at_eff_neg, None, None, is_at_fact)
        action.run_effect(is_at_eff, None, None, None)

        is_at_fact = next(filter(lambda x: x.name == predicate_factory.get("is-at"), problem.init)) 
        is_at_goal = next(filter(lambda x: x.name == predicate_factory.get("is-at"), problem.goal)) 
        problem.match_goal_condition(is_at_fact, is_at_goal)
        problem.match_goal()
    except AssertionError:
        return
    raise AssertionError("Can't be solvable")

