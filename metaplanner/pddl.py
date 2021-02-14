from collections import defaultdict
import sys
import re
import string
from itertools import zip_longest
import metaplanner.planner

# sys.path.append(".")
from metaplanner.planner import Predicate, Action, Problem, Domain, Object, PredicateId, Parameter, PDDLClass, EQ_PREDICATE

DEBUG = False

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

def list_to_lisp(v):
    if hasattr(v,"asList"): v=v.asList()
    if not "(" in repr(v):
        return repr(v).replace("[","(").replace("]",")").replace("'","").replace(",","")\
        .replace("\"","").replace(" {}","")#.replace("((","(").replace("))",")")
    else:
        return v

# class ListLike(list):
#     def asList(self):
#         return self

filt = re.compile("^"+string.ascii_letters+string.digits+"-_:=")
transr = re.compile("([^\\[^\\]^\\s]+)")

def lisp_to_list(v):
    return [eval(",".join(transr.sub(r'"\1"' ,filt.sub('',v).replace("(","[").replace(")","]")).split()))]


class PDDLClassFactory:
    classes: dict

    def __init__(self):
        self.classes = {}
    
    def create(self, classname):
        if classname in self.classes:
            return  # Refusing to rewrite class...
        self.classes[classname] = PDDLClass()
        if DEBUG:
            self.classes[classname]._name = classname

    def get(self, classname):
        return self.classes[classname]


class PDDLObjectFactory:
    objects: dict
    class_factory: PDDLClassFactory

    def __init__(self, class_factory=None):
        self.objects = {}
        self.class_factory = class_factory
        self.obj_name_map = {}
        self.objects_perclass = defaultdict(list)

    def create(self, oname, clsname):
        assert not oname.startswith("?")
        self.objects[oname] = Object(self.class_factory.get(clsname))
        if DEBUG:
            self.objects[oname]._classname = clsname
        self.obj_name_map[self.objects[oname]] = oname
        self.objects_perclass[clsname].append(oname)

    def get(self, obj_name, classname="object"):
        return self.objects[obj_name]
    
    def to_name(self, obj):
        return self.obj_name_map[obj]


class PredicateFactory:
    predicates: dict
    
    def __init__(self):
        self.predicates = {}
        self.predicates["="] = EQ_PREDICATE

    def create(self, pred_name):
        assert pred_name not in self.predicates
        self.predicates[pred_name] = PredicateId()
        self.predicates[pred_name].name = pred_name
    
    def get(self, pred_name):
        return self.predicates[pred_name]


class ParameterFactory:
    parameters: dict
    obj_name_map: dict
    objects: PDDLObjectFactory
    classes: PDDLClassFactory

    def __init__(self, objectFactory, classFactory):
        self.parameters = {}
        self.objects = objectFactory
        self.obj_name_map = {}
        self.classes = classFactory
    
    def create(self, pname, clsname):
        assert pname.startswith("?")
        self.parameters[pname] = Parameter(self.classes.get(clsname))
        self.obj_name_map[self.parameters[pname]] = pname
        if DEBUG:
            self.parameters[pname]._name = pname
            self.parameters[pname]._clsname = clsname
    
    def get(self, par_name):
        if not par_name in self.parameters and not par_name.startswith("?"):
            # If this is an object, create a constant parameter
            self.parameters[par_name] = Parameter(self.objects.get(par_name)._class)
            self.parameters[par_name].const = True
            self.parameters[par_name].obj = self.objects.get(par_name)
            self.obj_name_map[self.parameters[par_name]] = par_name
        print("Returning prarameter", par_name, self.parameters[par_name])
        return self.parameters[par_name]
    
class ActionFactory:
    name_action_map: dict
    action_name_map: dict
    
    def __init__(self, problem):
        self.name_action_map = {}
        self.action_name_map = {}
        self.problem = problem
    
    def get(self, name):
        if name in self.name_action_map:
            return self.name_action_map[name]
        self.name_action_map[name] = Action(self.problem)
        self.action_name_map[self.name_action_map[name]] = name
        return self.name_action_map[name]
    
    def to_name(self, action_obj):
        return self.action_name_map[action_obj]
        

def fill_pkeys(p1, p2, negated):
    pred_init = {}
    if isinstance(p1, Parameter):
        pred_init["p1"] = p1
    else:
        pred_init["obj_1"] = p1
    if p2 is not None:
        if isinstance(p2, Parameter):
            pred_init["p2"] = p2
        else:
            pred_init["obj_2"] = p2
    else:
        pred_init["parity"] = 1
    pred_init["negated"] = negated
    print("Returning", repr(pred_init))
    return pred_init


def parse_pddl_text(domain_str, problem_str):
    domain_lisp = lisp_to_list(domain_str)
    problem_lisp = lisp_to_list(problem_str)

    predicate_factory = PredicateFactory()
    class_factory = PDDLClassFactory()
    object_factory = PDDLObjectFactory(class_factory)
    parameter_factories = {}

    # We need to create problem first because it will be needed by action init
    domain = Domain()
    problem = Problem()
    action_factory = ActionFactory(problem)

    typed_pddl = False 

    for l in domain_lisp[0]:
        if type(l) != list: continue
        elif l[0] == ":requirements":
            if ":typing" in l:
                typed_pddl = True
            else:
                typed_pddl = False
        elif l[0] == ":predicates":
            predicates = l[1:]
            for predicate in predicates:
                pred_name = predicate[0]
                predicate_factory.create(pred_name)

    for l in problem_lisp[0]:
        print("Parsing line", l)
        if l[0] == ":objects":
            # TODO: generate objects
            state = "object"
            cur_cls = None
            objec_names = []
            for o in l[1:]:
                if o == "-":
                    state = "class"
                    continue
                if state == "class":
                    # o now is object class
                    cur_cls = o
                    for oname in objec_names:
                        print("Adding object", oname, cur_cls)
                        class_factory.create(cur_cls)
                        object_factory.create(oname, cur_cls)
                    objec_names = []
                    state = "object"
                    continue
                if state == "object":
                    objec_names.append(o)
        if l[0] == ":init":
            for pfact in l[1:]:
                predicate_id = predicate_factory.get(pfact[0])
                v1 = object_factory.get(pfact[1])
                if len(pfact) == 3:
                    v2 = object_factory.get(pfact[2])
                    fact = Predicate(predicate_id, obj_1=v1, obj_2=v2, parity=2)
                else:
                    fact = Predicate(predicate_id, obj_1=v1, parity=1)
                problem.init.add(fact)
                print("Added init state")
        if l[0] == ":goal":
            for pfact in l[1][1:]:  # skip and...
                predicate_id = predicate_factory.get(pfact[0])
                v1 = object_factory.get(pfact[1])
                if len(pfact) == 3:
                    v2 = object_factory.get(pfact[2])
                    fact = Predicate(predicate_id, obj_1=v1, obj_2=v2, parity=2)
                else:
                    fact = Predicate(predicate_id, obj_1=v1, parity=1)
                print("adding goal")
                problem.add_goal(fact)


    for l in domain_lisp[0]:
        # print("Parsing line", l)
        if type(l) != list: continue
        elif l[0] == ":action":
            action = l
            action_name = action[1]
            # action_obj = Action(action_name, problem)
            # action_obj = Action(problem)
            action_obj = action_factory.get(action_name)
            domain.actions.add(action_obj)
            print("Adding action", action_name)
            preconditions = action[5][1:] # skip (and ...)
            pf = ParameterFactory(object_factory, class_factory)
            parameters = action[3]
            for par, _, cls_ in grouper(parameters, 3):
                assert par is not None and cls_ is not None
                pf.create(par, cls_)
            parameter_factories[action_name] = pf
            for precondition in preconditions:
                if precondition[0] == "not":
                    precondition_name = predicate_factory.get(precondition[1][0])
                    p1=pf.get(precondition[1][1])
                    if len(precondition[1]) == 3:
                        p2 = pf.get(precondition[1][2])
                    else:
                        p2 = None
                    pkeys = fill_pkeys(p1, p2, True)
                else:
                    precondition_name = predicate_factory.get(precondition[0])
                    p1=pf.get(precondition[1])
                    if len(precondition) == 3:
                        p2 = pf.get(precondition[2])
                    else:
                        p2 = None
                    pkeys = fill_pkeys(p1, p2, False)
                precondition_obj = Predicate(precondition_name, **pkeys) 
                action_obj.add_precondition(precondition_obj)
            effects = action[7][1:]
            for effect in effects:
                if effect[0] == "not":
                    eff_name = predicate_factory.get(effect[1][0])
                    p1=pf.get(effect[1][1])
                    if len(effect[1]) == 3:
                        p2 = pf.get(effect[1][2])
                    else:
                        p2 = None
                    pkeys = fill_pkeys(p1, p2, True)
                else:
                    eff_name = predicate_factory.get(effect[0])
                    p1=pf.get(effect[1])
                    if len(effect) == 3:
                        p2 = pf.get(effect[2])
                    else:
                        p2 = None
                    pkeys = fill_pkeys(p1, p2, False)
                effect_obj = Predicate(eff_name, **pkeys) 
                action_obj.add_effect(effect_obj)
    
    dump_task(domain, problem, action_factory, predicate_factory, object_factory)

    problem._tracer = metaplanner.planner.PlanTracer(object_factory=object_factory, action_factory=action_factory, parameter_factory=parameter_factories)

    return domain, problem, predicate_factory, object_factory, parameter_factories, action_factory
    
def dump_task(domain, problem, action_factory: ActionFactory, predicate_factory=None, object_factory=None):
    for act in domain.actions:
        print("- Action", action_factory.to_name(act))
        print("  Preconditions", act.pre_count)
        print("  Effects", act.eff_count)
        for pre in act.precondition:
            print(" -- Precondition:", id(pre), "negated", pre.negated)
        for eff in act.effect:
            print(" -- Effect:", id(eff), "negated", eff.negated)
    for fact in problem.init:
        print("- Init", fact, id(fact))
    print("- Goal count", problem.goal_count)
    for goal in problem.goal:
        print("- Goal:", goal, id(goal))
    