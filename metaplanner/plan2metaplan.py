import sys
import json
import metaplanner.pddl as pd
import metaplanner.planner
import typing
import collections

def load_hints(splan, action_factory: pd.ActionFactory, parameter_factories: typing.Dict[str, pd.ParameterFactory], 
               object_factory: pd.PDDLObjectFactory):
    precondition_hints = collections.defaultdict(list)
    effect_hints = collections.defaultdict(list)
    plan_len = 0
    for l in splan.split("\n"):
        if len(l) < 3: continue
        if ";" in l: continue
        l = l.strip()
        l = l.replace("(", "").replace(")", "")
        l = l.split()
        action_name = l[0]
        parameters_objects = l[1:]

        pf = parameter_factories[action_name]

        # Because we don't know which fact it chose to match,
        # We can't know which of the objects actually were matched simulatenously
        # So we can only assume that WHENEVER they match, we know which predicate matches
        #   which object from its places
        # (action-name obj1 obj2 obj3)

        par_pddl_ids = list(zip(pf.parameters.keys(), parameters_objects))
        # print("Hints for line", l)
        # print(par_pddl_ids)

        hint_cnt = 0
        for parname, objid in par_pddl_ids:
            for precond in action_factory.name_action_map[action_name].precondition:
                if precond.par_1 == parameter_factories[action_name].parameters[parname]:
                    pred_obj = precond
                    par_obj = object_factory.objects[objid]
                    # TODO: add action object (when many actions)
                    if pred_obj.name == metaplanner.planner.EQ_PREDICATE:
                        precondition_hints["pred-eq-obj1"].append((pred_obj, par_obj))
                    else:
                        precondition_hints["pred-obj1"].append((pred_obj, par_obj))
                    hint_cnt += 1
                if precond.par_2 == parameter_factories[action_name].parameters[parname]:
                    pred_obj = precond
                    par_obj = object_factory.objects[objid]
                    if pred_obj.name == metaplanner.planner.EQ_PREDICATE:
                        precondition_hints["pred-eq-obj2"].append((pred_obj, par_obj))
                    else:
                        precondition_hints["pred-obj2"].append((pred_obj, par_obj))
                    hint_cnt += 1
            for precond in action_factory.name_action_map[action_name].effect:
                print("HINTS checking effect", precond)
                if precond.par_1 == parameter_factories[action_name].parameters[parname]:
                    print("HINTS found par 1 in effect", action_name, parname, "=", objid)
                    pred_obj = precond
                    par_obj = object_factory.objects[objid]
                    effect_hints["eff-obj1"].append((plan_len, pred_obj, par_obj))
                    # TODO: add action object (when many actions)
                    hint_cnt += 1
                if precond.par_2 == parameter_factories[action_name].parameters[parname]:
                    print("HINTS found par 2 in effect", action_name, parname, "=", objid)
                    pred_obj = precond
                    par_obj = object_factory.objects[objid]
                    effect_hints["eff-obj2"].append((plan_len, pred_obj, par_obj))
                    hint_cnt += 1
        plan_len += 1

        # print(hints)
    print("Hints loaded:", hint_cnt)
    return precondition_hints, effect_hints


