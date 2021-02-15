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

        assert len(list(pf.parameters.keys())) == len(parameters_objects)

        par_pddl_ids = list(zip(pf.parameters.keys(), parameters_objects))
        print("Hints for line", l, par_pddl_ids)
        action_obj = action_factory.name_action_map[action_name]
        hint_cnt = 0
        for parname, objid in par_pddl_ids:
            for precond in action_factory.name_action_map[action_name].precondition:
                pred_obj = precond
                par_obj = object_factory.objects[objid]
                # precondition_hints["pred-obj1"].append((plan_len, action_obj, pred_obj, par_obj))
                # precondition_hints["pred-obj2"].append((plan_len, action_obj, pred_obj, par_obj))
                # precondition_hints["pred-obj1-cln"].append((action_obj, pred_obj, par_obj))
                # precondition_hints["pred-obj1-cln"].append((action_obj, pred_obj, par_obj))
                # precondition_hints["pred-obj1"].append((plan_len, action_obj, pred_obj, metaplanner.planner.OBJ_NONE))
                # precondition_hints["pred-obj2"].append((plan_len, action_obj, pred_obj, metaplanner.planner.OBJ_NONE))
                # precondition_hints["pred-obj1-cln"].append((action_obj, pred_obj, metaplanner.planner.OBJ_NONE))
                # precondition_hints["pred-obj1-cln"].append((action_obj, pred_obj, metaplanner.planner.OBJ_NONE))
                if precond.par_1 == parameter_factories[action_name].parameters[parname]:
                    if pred_obj.name == metaplanner.planner.EQ_PREDICATE:
                        assert pred_obj.par_1._class == par_obj._class
                        precondition_hints["pred-eq-obj1"].append((plan_len, action_obj, pred_obj, par_obj))
                        precondition_hints["pred-obj1-cln"].append((action_obj, pred_obj, par_obj))
                        precondition_hints["pred-obj1-cln"].append((action_obj, pred_obj, metaplanner.planner.OBJ_NONE))
                    else:
                        assert pred_obj.par_1._class == par_obj._class
                        precondition_hints["pred-obj1"].append((plan_len, action_obj, pred_obj, par_obj))
                        precondition_hints["pred-obj1-cln"].append((action_obj, pred_obj, par_obj))
                        precondition_hints["pred-obj1-cln"].append((action_obj, pred_obj, metaplanner.planner.OBJ_NONE))
                    hint_cnt += 1
                if precond.par_2 == parameter_factories[action_name].parameters[parname]:
                    if pred_obj.name == metaplanner.planner.EQ_PREDICATE:
                        assert pred_obj.par_2._class == par_obj._class
                        precondition_hints["pred-eq-obj2"].append((plan_len, action_obj, pred_obj, par_obj))
                        precondition_hints["pred-obj2-cln"].append((action_obj, pred_obj, par_obj))
                        precondition_hints["pred-obj2-cln"].append((action_obj, pred_obj, metaplanner.planner.OBJ_NONE))
                    else:
                        assert pred_obj.par_2._class == par_obj._class
                        precondition_hints["pred-obj2"].append((plan_len, action_obj, pred_obj, par_obj))
                        precondition_hints["pred-obj2-cln"].append((action_obj, pred_obj, par_obj))
                        precondition_hints["pred-obj2-cln"].append((action_obj, pred_obj, metaplanner.planner.OBJ_NONE))
                    hint_cnt += 1
            for precond in action_factory.name_action_map[action_name].effect:
                print("HINTS checking effect", precond)
                pred_obj = precond
                par_obj = object_factory.objects[objid]
                # effect_hints["eff-obj1"].append((plan_len, action_obj, pred_obj, par_obj))
                # effect_hints["eff-obj2"].append((plan_len, action_obj, pred_obj, par_obj))
                # effect_hints["eff-obj1-cln"].append((action_obj, pred_obj, par_obj))
                # effect_hints["eff-obj2-cln"].append((action_obj, pred_obj, par_obj))
                # effect_hints["eff-obj1"].append((plan_len, action_obj, pred_obj, metaplanner.planner.OBJ_NONE,))
                # effect_hints["eff-obj2"].append((plan_len, action_obj, pred_obj, metaplanner.planner.OBJ_NONE,))
                # effect_hints["eff-obj1-cln"].append((action_obj, pred_obj, metaplanner.planner.OBJ_NONE,))
                # effect_hints["eff-obj2-cln"].append((action_obj, pred_obj, metaplanner.planner.OBJ_NONE,))
                if precond.par_1 == parameter_factories[action_name].parameters[parname]:
                    print("HINTS found par 1 in effect", action_name, parname, "=", objid)
                    pred_obj = precond
                    par_obj = object_factory.objects[objid]
                    assert pred_obj.par_1._class == par_obj._class
                    effect_hints["eff-obj1"].append((plan_len, action_obj, pred_obj, par_obj))
                    effect_hints["eff-obj1-cln"].append((action_obj, pred_obj, par_obj,))
                    effect_hints["eff-obj1-cln"].append((action_obj, pred_obj, metaplanner.planner.OBJ_NONE,))
                    hint_cnt += 1
                if precond.par_2 == parameter_factories[action_name].parameters[parname]:
                    print("HINTS found par 2 in effect", action_name, parname, "=", objid)
                    pred_obj = precond
                    par_obj = object_factory.objects[objid]
                    assert pred_obj.par_2._class == par_obj._class
                    effect_hints["eff-obj2"].append((plan_len, action_obj, pred_obj, par_obj))
                    effect_hints["eff-obj2-cln"].append((action_obj, pred_obj, par_obj,))
                    effect_hints["eff-obj2-cln"].append((action_obj, pred_obj, metaplanner.planner.OBJ_NONE,))
                    hint_cnt += 1
            # TODO: calculate which branches went with NONE objects for cleaning
        # TODO HERE: Now add all the static hints for this plan len
        for precond in action_factory.name_action_map[action_name].precondition:
            pred_obj = precond
            if precond.par_1.const == True:
                par_obj = precond.par_1.obj
                if pred_obj.name == metaplanner.planner.EQ_PREDICATE:
                    assert pred_obj.par_1._class == par_obj._class
                    precondition_hints["pred-eq-obj1"].append((plan_len, action_obj, pred_obj, par_obj))
                    precondition_hints["pred-obj1-cln"].append((action_obj, pred_obj, par_obj))
                    precondition_hints["pred-obj1-cln"].append((action_obj, pred_obj, metaplanner.planner.OBJ_NONE))
                else:
                    assert pred_obj.par_1._class == par_obj._class
                    precondition_hints["pred-obj1"].append((plan_len, action_obj, pred_obj, par_obj))
                    precondition_hints["pred-obj1-cln"].append((action_obj, pred_obj, par_obj))
                    precondition_hints["pred-obj1-cln"].append((action_obj, pred_obj, metaplanner.planner.OBJ_NONE))
            if precond.par_2.const == True:
                par_obj = precond.par_2.obj
                if pred_obj.name == metaplanner.planner.EQ_PREDICATE:
                    assert pred_obj.par_2._class == par_obj._class
                    precondition_hints["pred-eq-obj2"].append((plan_len, action_obj, pred_obj, par_obj))
                    precondition_hints["pred-obj2-cln"].append((action_obj, pred_obj, par_obj))
                    precondition_hints["pred-obj2-cln"].append((action_obj, pred_obj, metaplanner.planner.OBJ_NONE))
                else:
                    assert pred_obj.par_2._class == par_obj._class
                    precondition_hints["pred-obj2"].append((plan_len, action_obj, pred_obj, par_obj))
                    precondition_hints["pred-obj2-cln"].append((action_obj, pred_obj, par_obj))
                    precondition_hints["pred-obj2-cln"].append((action_obj, pred_obj, metaplanner.planner.OBJ_NONE))
        for precond in action_factory.name_action_map[action_name].effect:
            pred_obj = precond
            if precond.par_1.const == True:
                par_obj = precond.par_1.obj
                assert pred_obj.par_1._class == par_obj._class
                effect_hints["eff-obj1"].append((plan_len, action_obj, pred_obj, par_obj))
                effect_hints["eff-obj1-cln"].append((action_obj, pred_obj, par_obj,))
                effect_hints["eff-obj1-cln"].append((action_obj, pred_obj, metaplanner.planner.OBJ_NONE,))
            if precond.par_2.const == True:
                par_obj = precond.par_2.obj
                assert pred_obj.par_2._class == par_obj._class
                effect_hints["eff-obj2"].append((plan_len, action_obj, pred_obj, par_obj))
                effect_hints["eff-obj2-cln"].append((action_obj, pred_obj, par_obj,))
                effect_hints["eff-obj2-cln"].append((action_obj, pred_obj, metaplanner.planner.OBJ_NONE,))
        plan_len += 1

        # print(hints)
    print("Hints loaded:", hint_cnt)
    return precondition_hints, effect_hints


