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

def test_action_twoactions():
    domain, problem, predicate_factory, object_factory, parameter_factories, action_factory \
        = parse_pddl_text(DOMAIN, PROBLEM)
    problem.prepare()

    action: Action = action_factory.get("random-action-268617")
    # match 2 preconditions
    pre1 = next(filter(lambda x: x.name == predicate_factory.get("rppred2"), action.precondition))

    fact1 = next(filter(lambda x: x.name == predicate_factory.get("rppred2") and\
           x.obj_1 == object_factory.get("rpobj2") and \
               x.obj_2 == object_factory.get("rpobj2"), problem.init)) 
    action.match_precondition(pre1, fact1)

    # run effect
    eff1 = next(filter(
        lambda x: x.name == predicate_factory.get("rppred3")
            and x.negated == False, action.effect)) 
    obj1 = object_factory.objects["rpobj2"]
    obj2 = object_factory.objects["rpobj4"]
    action.run_effect(eff1, obj1, obj2, None)

    eff2 = next(filter(
        lambda x: x.name == predicate_factory.get("rppred4")
            and x.negated == False, action.effect)) 
    obj1_4 = object_factory.objects["rpobj2"]
    # obj2 = object_factory.objects["rpobj4"]
    action.run_effect(eff2, None, obj1_4, None)

    # clean preconditions
    action.clean_precondition(pre1)
    # clean effect 
    action.clean_effect(eff1)
    action.clean_effect(eff2)

    # SECOND

    action: Action = action_factory.get("random-action-251873")
    # match 2 preconditions
    pre1 = next(filter(lambda x: x.name == predicate_factory.get("rppred4") and \
        x.par_1.obj == object_factory.get("rpobj4"), action.precondition))

    fact1 = next(filter(lambda x: x.name == predicate_factory.get("rppred4") and\
           x.obj_1 == object_factory.get("rpobj4") and \
               x.obj_2 == obj1_4, problem.init)) 
    action.match_precondition(pre1, fact1)


    pre2 = next(filter(lambda x: x.name == predicate_factory.get("rppred4") and \
        x.par_1.obj == object_factory.get("rpobj3"), action.precondition))

    fact2 = next(filter(lambda x: x.name == predicate_factory.get("rppred4") and\
           x.obj_1 == object_factory.get("rpobj3") and \
               x.obj_2 == object_factory.get("rpobj1"), problem.init)) 
    action.match_precondition(pre2, fact2)


    pre3 = next(filter(lambda x: x.name == predicate_factory.get("rppred4") and \
        x.par_1.obj != object_factory.get("rpobj3") and x.par_1.obj != object_factory.get("rpobj4"), 
        action.precondition))

    fact3 = next(filter(lambda x: x.name == predicate_factory.get("rppred4") and\
           x.obj_1 == object_factory.get("rpobj4") and \
               x.obj_2 == object_factory.get("rpobj2"), problem.init)) 
    action.match_precondition(pre3, fact3)

    # run effect
    eff1 = next(filter(
        lambda x: x.name == predicate_factory.get("rppred1")
            and x.negated == False, action.effect)) 
    obj2 = object_factory.objects["rpobj4"]
    action.run_effect(eff1, obj2, None, None)

    pre_hints, eff_hints = metaplanner.plan2metaplan.load_hints(PLAN, action_factory=action_factory, 
            parameter_factories=parameter_factories, object_factory=object_factory)
    metaplanner.hints.pre_hints = pre_hints
    metaplanner.hints.eff_hints = eff_hints
    # solve(problem.match_goal)


    return
    f1 = next(filter(lambda x: x.name == predicate_factory.get("rppred1") and \
            x.obj_2 == object_factory.get("rpobj2"), problem.init)) 
    g1 = next(filter(lambda x: x.name == predicate_factory.get("rppred1") and \
            x.obj_1 == object_factory.get("rpobj4") and 
            x.obj_2 == object_factory.get("rpobj2"), problem.goal)) 
    problem.match_goal_condition(f1, g1)
    problem.match_goal()

    return
    for step in PLAN.split("\n"):
        if len(step) < 5: continue
        if step.startswith(";"): continue
        step = step.strip()[1:-1].split()
        action = action_factory.get(step[0])
        # objects = [object_factory.get(x) for x in 

    for l in PLAN.split("\n"):
        if len(l) < 3: continue
        if ";" in l: continue
        l = l.strip()
        l = l.replace("(", "").replace(")", "")
        l = l.split()
        action_name = l[0]
        parameters_objects = l[1:]

        pf = parameter_factories[action_name]

        par_pddl_ids = list(zip(pf.parameters.keys(), parameters_objects))
        action_obj = action_factory.name_action_map[action_name]
        hint_cnt = 0
        for parname, objid in par_pddl_ids:
            for precond in action_factory.name_action_map[action_name].precondition:
                if precond.par_1 == parameter_factories[action_name].parameters[parname]:
                    pred_obj = precond
                    par_obj = object_factory.objects[objid]
                    if pred_obj.name == metaplanner.planner.EQ_PREDICATE:
                        pass
                    else:
                        pass
                    hint_cnt += 1
                if precond.par_2 == parameter_factories[action_name].parameters[parname]:
                    pred_obj = precond
                    par_obj = object_factory.objects[objid]
                    if pred_obj.name == metaplanner.planner.EQ_PREDICATE:
                        pass
                    else:
                        pass
                    hint_cnt += 1
            for precond in action_factory.name_action_map[action_name].effect:
                if precond.par_1 == parameter_factories[action_name].parameters[parname]:
                    pred_obj = precond
                    par_obj = object_factory.objects[objid]
                    # TODO: add action object (when many actions)
                    hint_cnt += 1
                if precond.par_2 == parameter_factories[action_name].parameters[parname]:
                    print("HINTS found par 2 in effect", action_name, parname, "=", objid)
                    pred_obj = precond
                    par_obj = object_factory.objects[objid]
                    hint_cnt += 1
            # TODO: calculate which branches went with NONE objects for cleaning
        plan_len += 1
    return

    
    

    print(problem._tracer.str_plan())