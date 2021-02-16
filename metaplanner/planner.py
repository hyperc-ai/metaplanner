from hyperc import solve, side_effect, side_effect_decorator, hint_exact
import copy
import metaplanner.hints as hintsmod


class LinkedListItem:
    next: "LinkedListItem"
    item: str

    def __init__(self):
        self.item = ""


class PlanTracer:
    def __init__(self, object_factory, action_factory, parameter_factory):
        self.collected_items = []
        self.plan = []
        self.action_factory = action_factory
        self.object_factory = object_factory
        self.parameter_factory = parameter_factory
    
    def insert(self, par, obj):
        self.collected_items.append([par, obj])
    
    def fire(self, action_obj):
        self.plan.append([action_obj, self.collected_items])
        self.collected_items = []

    def set_current_action(self, action_obj):
        self.current_action = action_obj
    
    def str_plan(self):
        if len(self.collected_items) > 0:  # run incomplete effect
            self.fire(self.current_action)
        lplan = []
        for step in self.plan:
            action_name = self.action_factory.to_name(step[0])
            all_params_k = self.parameter_factory[action_name].obj_name_map.items()
            all_params = {}
            for k, v in all_params_k:
                if not str(v).startswith("?"): continue
                all_params[k] = "None-"+str(v)
            for par, obj in step[1]:
                all_params[par] = self.object_factory.to_name(obj)
            match_objects = " ".join(all_params.values())
            lplan.append(f"({action_name} {match_objects})")
        lplan.append(f"; cost = {len(lplan)} (unit cost)")
        return "\n".join(lplan)


class LinkedList:
    head: LinkedListItem
    next: LinkedListItem

    def __init__(self):
        self.next = LinkedListItem()
        self.head = self.next
    
    def append(self, s: str):
        new_item = LinkedListItem()
        self.next.item = s
        self.next.next = new_item
        self.next = new_item


class PDDLClass:
    # name: str
    def __init__(self):
        pass
        # self.name = ""

class Object:
    # name: str
    _class: PDDLClass
    def __init__(self, _class: PDDLClass):
        self._class = _class
        # self.name = "<NONAME OBJECT>"

        
NONE_CLASS = PDDLClass()
OBJ_NONE = Object(NONE_CLASS)
# OBJ_NONE.name = "NONE_OBJECT"

class Parameter:
    obj: Object
    _class: PDDLClass
    const: bool
    # name: str

    def __init__(self, _class: PDDLClass):
        # self.name = ""
        self.obj = OBJ_NONE
        self._class = _class
        self.const = False

PAR_NONE = Parameter(NONE_CLASS)
PAR_NONE.obj = OBJ_NONE

class PredicateId:
    # name: str
    def __init__(self):
        # self.name = ""    
        pass


EQ_PREDICATE = PredicateId()

class Fact:
    name: PredicateId
    obj_1: Object
    obj_2: Object
    matched: bool
    def __init__(self, name: PredicateId, obj_1:Object=OBJ_NONE, obj_2:Object=OBJ_NONE):
        self.name = name
        self.obj_1 = obj_1
        self.obj_2 = obj_2
        self.matched = False


class Predicate:
    name: PredicateId

    par_1: Parameter
    par_2: Parameter

    negated: bool
    matched: bool

    def __init__(self, name: PredicateId,  
                 p1:Parameter=PAR_NONE, p2:Parameter=PAR_NONE, negated:bool=False):
        self.name = name
        self.negated = negated
        self.matched = False
        self.par_1 = p1
        self.par_2 = p2
        # side_effect(lambda: print(f" - ({self.name.name} {self.obj_1.name} {self.obj_2.name} {self.par_1.name} {self.par_2.name}) negated = {self.negated}"))


class Action:
    # name: str
    next_action: "Action"
    pre_count: int
    eff_count: int

    parameters: set
    precondition: set
    effect: set

    pre_match: int
    eff_match: int
    eff_run: int

    pre_completed: bool
    eff_completed: bool

    problem: "Problem"

    def __init__(self, problem: "Problem"):
    # def __init__(self, name, problem: "Problem"):
        # self.name = name
        self.pre_count = 0
        self.eff_count = 0
        self.eff_completed = False
        self.pre_completed = False
        self.parameters = set()
        self.precondition = set()
        self.effect = set()
        self.pre_match = 0
        self.eff_match = 0
        self.eff_run = 0
        self.problem = problem
    
    def add_precondition(self, p: Predicate):
        problem = self.problem
        assert 0 in problem.current_actions
        side_effect(lambda: print(f"add_precondition:"))
        self.precondition.add(p)
        self.pre_count += 1

    
    def add_effect(self, p: Predicate):
        assert 0 in self.problem.current_actions
        self.effect.add(p)
        self.eff_count += 1
        side_effect(lambda: print(f"add_effect:"))


    def match_precondition(self, pred: Predicate, fact: Fact):
        "Match some of our precondition"
        problem = self.problem

        # block to reduce branching
        assert self.effect != problem.init
        # assert problem.init != problem.current_actions
        # assert problem.current_actions != self.effect
        # end_block

        assert self.eff_completed != True
        assert self.pre_completed != True
        assert problem.goal_matched == 0
        assert pred in self.precondition, "`pred` must be from preconditions"
        assert fact in problem.init, "`fact` must exist in problem fact space"
        assert pred.name == fact.name, "Can only match same fact"
        assert pred.negated == False 
        assert self.problem.plan_len != -1

        if pred.par_1.obj == OBJ_NONE:
            pred.par_1.obj = fact.obj_1
            side_effect(lambda: self.problem._tracer.insert(pred.par_1, fact.obj_1))
        hint_exact(self.problem.plan_len, self, pred, pred.par_1.obj, lambda: _real_globals_dict["hintsmod"].pre_hints.get("pred-obj1"))
        
        if pred.par_2.obj == OBJ_NONE:
            pred.par_2.obj = fact.obj_2
            side_effect(lambda: self.problem._tracer.insert(pred.par_2, fact.obj_2))
        hint_exact(self.problem.plan_len, self, pred, pred.par_2.obj, lambda: _real_globals_dict["hintsmod"].pre_hints.get("pred-obj2"))

        assert fact.obj_1 == pred.par_1.obj
        assert fact.obj_1._class == pred.par_1.obj._class

        assert fact.obj_2 == pred.par_2.obj
        assert fact.obj_2._class == pred.par_2.obj._class

        assert pred.matched == False

        pred.matched = True
        self.pre_match += 1
        if self.pre_match == self.pre_count:
            # problem.current_actions.add(2)
            self.pre_completed = True
        side_effect(lambda: print(f"match_precondition {pred.name},{pred.par_1.obj}, {pred.par_2.obj}"))
        # side_effect(lambda: print(f"match_precondition {pred.name.name},{pred.par_1.obj.name}, {pred.par_2.obj.name}"))

    def match_NOT_precondition_when_direct_link(self, pred: Predicate, fact: Fact):
        "Match NOT precondition. Has a limited support in HyperC PDDL dialect"
        # side_effect(lambda: print(f"match_NOT_precondition_when_direct_link {pred.name.name},{pred.par_1.obj.name}, {pred.par_2.obj.name}"))
        side_effect(lambda: print(f"match_NOT_precondition_when_direct_link {pred.name},{pred.par_1.obj}, {pred.par_2.obj}"))
        problem = self.problem

        # block to reduce branching 
        assert self.effect != problem.init
        # assert problem.init != problem.current_actions
        # assert problem.current_actions != self.effect
        # end_block
        assert self.eff_completed != True
        assert self.pre_completed != True

        assert problem.goal_matched == 0
        assert pred in self.precondition, "`pred` must be from preconditions"
        assert fact in problem.init, "`fact` with another value must exist in problem fact space"
        assert pred.name == fact.name, "Can only match same fact"
        assert pred.negated == True        
        assert pred.matched == False
        assert fact.obj_1 == pred.par_1.obj
        assert fact.obj_1._class == pred.par_1.obj._class
        assert fact.obj_2._class == pred.par_2.obj._class
        assert fact.obj_2 != pred.par_2.obj
        pred.matched = True
        self.pre_match += 1
        if self.pre_match == self.pre_count:
            # problem.current_actions.add(2)
            self.pre_completed = True

    def match_eq_precondition(self, pre: Predicate):
        problem = self.problem

        # block to reduce branching 
        assert self.effect != problem.init
        # assert problem.init != problem.current_actions
        # assert problem.current_actions != self.effect
        # end_block

        assert self.eff_completed != True
        assert self.pre_completed != True
        assert problem.goal_matched == 0
        assert pre.matched == False
        assert pre in self.precondition, "`pred` must be from preconditions"
        assert pre.matched == False
        assert pre.name == EQ_PREDICATE
        assert pre.par_1.obj != OBJ_NONE
        assert pre.par_2.obj != OBJ_NONE
        assert self.problem.plan_len != -1
        hint_exact(self.problem.plan_len, self, pre, pre.par_1.obj, lambda: _real_globals_dict["hintsmod"].pre_hints.get("pred-eq-obj1"))
        hint_exact(self.problem.plan_len, self, pre, pre.par_2.obj, lambda: _real_globals_dict["hintsmod"].pre_hints.get("pred-eq-obj2"))
        if pre.negated == True:
            assert pre.par_1.obj != pre.par_2.obj
        else:
            assert pre.par_1.obj == pre.par_2.obj
        self.pre_match += 1
        pre.matched = True
        if self.pre_match == self.pre_count:
            # problem.current_actions.add(2)
            self.pre_completed = True

    def run_effect(self, eff: Predicate, obj1: Object, obj2: Object,
                   existing_fact: Fact):
        problem = self.problem

        # block to reduce branching 
        assert self.effect != problem.init
        # assert problem.init != problem.current_actions
        # assert problem.current_actions != self.effect
        # end_block

        assert self.eff_completed != True
        assert self.pre_completed == True
        # assert 2 in self.problem.current_actions
        assert problem.goal_matched == 0
        assert self.problem.plan_len != -1  # to expose plan_len
        # assert self.pre_match > 0
        assert self.pre_match == self.pre_count
        assert eff in self.effect
        assert eff.matched == False
        eff.matched = True
        side_effect(lambda: self.problem.plan.append(self if self.eff_match == 0 else None))
        side_effect(lambda: self.problem._tracer.set_current_action(self))
        # if self.eff_match == 0:  # TODO: remove this because it creates spurious branches
            # side_effect(lambda: self.problem.plan.append(self))  # TODO: PERF
            # self.problem.plan.append(self.name)  # TODO: PERF
        assert self.eff_match < self.eff_count
        self.eff_match += 1
        if eff.par_1.obj == OBJ_NONE:
            assert eff.par_1._class == obj1._class
            eff.par_1.obj = obj1
            side_effect(lambda: self.problem._tracer.insert(eff.par_1, obj1))
        hint_exact(self.problem.plan_len, self, eff, eff.par_1.obj, lambda: _real_globals_dict["hintsmod"].eff_hints.get("eff-obj1"))
        # TODO: do we need to support freevar effects?
        if eff.par_2.obj == OBJ_NONE:
            assert eff.par_2._class == obj2._class
            eff.par_2.obj = obj2
            side_effect(lambda: self.problem._tracer.insert(eff.par_2, obj2))
        hint_exact(self.problem.plan_len, self, eff, eff.par_2.obj, lambda: _real_globals_dict["hintsmod"].eff_hints.get("eff-obj2"))
        # If negated, remove, if non-negated: add
        # side_effect(lambda: print(f"run_effect {eff.name.name},{eff.par_1.obj.name},{eff.par_2.obj.name} - {existing_fact}"))       
        side_effect(lambda: print(f"run_effect {eff.name},{eff.par_1.obj},{eff.par_2.obj} - {existing_fact}"))       
        if eff.negated == True:
            assert existing_fact.name == eff.name
            assert existing_fact.obj_1 == eff.par_1.obj
            assert existing_fact.obj_1._class == eff.par_1.obj._class
            # TODO HERE: add hints to negation
            # TODO: support removing non-existing fact
            assert existing_fact.obj_2 == eff.par_2.obj
            assert existing_fact.obj_2._class == eff.par_2.obj._class
            problem.init.remove(existing_fact)
        else:
            hint_exact(self.problem.plan_len, self, eff, eff.par_1.obj, lambda: _real_globals_dict["hintsmod"].eff_hints.get("eff-obj1"))
            hint_exact(self.problem.plan_len, self, eff, eff.par_2.obj, lambda: _real_globals_dict["hintsmod"].eff_hints.get("eff-obj2"))
            problem.init.add(Fact(name=eff.name, obj_1=eff.par_1.obj, obj_2=eff.par_2.obj))
        if self.eff_match == self.eff_count:
            # problem.current_actions.add(3)
            self.eff_completed = True
            side_effect(lambda: self.problem._tracer.fire(self))

        # side_effect(lambda: print(f"Running action {self.name}"))
    # def clean_parameter(self, par: Parameter):
        # block to reduce branching 
        # assert self.effect != self.problem.init
        # assert self.problem.init != self.problem.current_actions
        # assert self.problem.current_actions != self.effect
        # end_block

        # assert par.const == False
        # assert self.eff_match > 0
        # assert 3 in self.problem.current_actions
        # par.obj = OBJ_NONE
        # side_effect(lambda: print(f"clean_parameter {par}"))
        
    def clean_precondition(self, pred: Predicate):
        assert pred in self.precondition
        # assert self.pre_match > 0
        # assert self.eff_match > 0
        assert pred.matched == True
        assert self.eff_completed == True
        assert self.pre_completed == True
        # assert 3 in self.problem.current_actions
        # TODO: clean precondition only when all parameters are cleaned
        # TODO: if/else for constant parameters that don't need to be cleaned
        # assert act.eff_match > 0
        pred.matched = False
        self.pre_match -= 1
        if pred.par_1.const != True:
            hint_exact(self, pred, pred.par_1.obj, lambda: _real_globals_dict["hintsmod"].pre_hints.get("pred-obj1-cln"))
            pred.par_1.obj = OBJ_NONE
        if pred.par_2.const != True:
            hint_exact(self, pred, pred.par_2.obj, lambda: _real_globals_dict["hintsmod"].pre_hints.get("pred-obj2-cln"))
            pred.par_2.obj = OBJ_NONE
        # if 2 in self.problem.current_actions:
            # self.problem.current_actions.remove(2)
        if self.pre_match == 0:
            self.pre_completed = False
        side_effect(lambda: print(f"clean_precondition {pred.name}"))

    def clean_effect(self, pred: Predicate):
        assert pred in self.effect
        assert self.problem.goal_matched == 0
        assert self.eff_completed == True
        assert self.pre_completed == False
        # assert act.eff_match > 0
        # assert act.pre_match > 0
        pred.matched = False
        self.eff_match -= 1
        if pred.par_1.const != True:
            hint_exact(self, pred, pred.par_1.obj, lambda: _real_globals_dict["hintsmod"].eff_hints.get("eff-obj1-cln"))
            pred.par_1.obj = OBJ_NONE
        if pred.par_2.const != True:
            hint_exact(self, pred, pred.par_2.obj, lambda: _real_globals_dict["hintsmod"].eff_hints.get("eff-obj2-cln"))
            pred.par_2.obj = OBJ_NONE
        # if 2 in self.problem.current_actions:
            # self.problem.current_actions.remove(2)
        if self.eff_match == 0:
            self.eff_completed = False
            self.problem.plan_len += 1
        side_effect(lambda: print(f"clean_eff {pred.name}"))

"""
    def finish_action(self, pred: Predicate, eff: Predicate):
        assert self.eff_match == 0
        assert self.pre_match == 0
        assert self.problem.goal_matched == 0
        assert pred.matched == False
        assert eff.matched == False
        # assert pred in self.precondition
        # assert eff in self.effect
        side_effect(lambda: print(f"finish_action {self}"))

    def execute(self, prev: "Action"):
        assert self.pre_match == self.pre_count
        assert self.eff_run == self.eff_count
        assert 4 in self.problem.current_actions
        prev.next_action = self
        side_effect(lambda: print(f"execute {self}"))
"""


class Domain:
    actions: set  # actions defined in domain
    def __init__(self):
        self.actions = set()

class Problem:
    init: set  # initial fact space
    goal: set  # the goal state predicate
    goal_count: int
    goal_matched: int
    action_implementation_started: bool
    solving_started: bool
    current_actions: set
    plan: LinkedList
    plan_len: int

    def __init__(self):
        self.init = set()
        self.goal = set()
        self.goal_count = 0
        self.goal_matched = 0
        self.action_implementation_started = False
        self.solving_started = False  # Init for 1-off run
        self.current_actions = set()
        self.current_actions.add(0)
        self.current_actions.add(1)
        self.plan = LinkedList()
        self.plan_len = 0

    def add_goal(self, goal_pred: Predicate):
        problem = self
        assert problem.solving_started == False
        self.goal.add(goal_pred)
        self.goal_count += 1

    def match_goal_condition(self, p: Fact, g: Fact):
        problem = self

        # block to reduce branching
        assert p != g 
        assert problem.init != problem.goal
        # end_block

        assert p in problem.init
        assert g in problem.goal
        assert p.name == g.name
        assert p.obj_1 == g.obj_1
        assert p.obj_2 == g.obj_2
        assert g.matched == False
        problem.goal_matched += 1
        problem.action_implementation_started == False
        g.matched = True
        side_effect(lambda: print(f"Problem  condition satisfied! {p.name} - {p.obj_1} - {p.obj_2} "))

    def match_goal(self):
        problem = self
        assert problem.goal_matched == problem.goal_count
        print("Problem solved!")
    
    @side_effect_decorator
    def prepare(self):
        self.solving_started = True
        self.current_actions.remove(0)
        # solve(self.match_goal)
