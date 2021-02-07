import random
import sys
import collections
import subprocess
# Generate "apples" simple problem variations


MIN_ACTION_PARAMS = 3
MAX_ACTION_PARAMS = 7

MIN_ACTION_PREDICATES = 2
MAX_ACTION_PREDICATES = 4

MIN_ACTIONS = 2
MAX_ACTIONS = 5

MIN_CLASSES = 2
MAX_CLASSES = 5

MIN_OBJECTS_PERCLASS = 1
MAX_OBJECTS_PERCLASS = 4

class PredicateDeclaration:
    pname: str
    arity: int
    p1class: str
    p2class: str

    def __init__(self, p1class, p2class, arity=2):
        self.pname = gen_random_predicate_name()
        self.arity = arity
        self.p1class = p1class
        self.p2class = p2class
    
    def __str__(self):
        if self.arity == 1:
            return f"({self.pname} ?v1 - {self.p1class})"
        else:
            return f"({self.pname} ?v1 - {self.p1class} ?v2 - {self.p2class})"
        

pred_id = 0


def gen_random_predicate_name():
    global pred_id
    pred_id += 1
    return f"rppred{pred_id}"


def gen_random_predicates_defs(classes_list):
    predicates = []
    for _ in range(random.randint(3, 4)):
        predicates.append(PredicateDeclaration(random.choice(classes_list), random.choice(classes_list)))
    return predicates


def rcv(name, idx=0):
    "Generate a random var-obj"
    return f"?{name}-{idx}"


def gen_parameters(l_objects):
    parameters = []
    for obj in l_objects:
        if obj.startswith("?"):
            classname = obj[1:].split("-")[0]
            parameters.append(f"{obj} - {classname}")
    return " ".join(parameters)


def gen_random_action(classes_list, objects_dict, precondition_decl):
    "Generate working action"

    # generate random parameters list to use

    objects_used = set()

    parameters_map = collections.defaultdict(list)  # Contain map of all parameters of this class

    i = 0
    for i in range(random.randint(MIN_ACTION_PARAMS, MAX_ACTION_PARAMS)):
        pclass = random.choice(classes_list)
        par_or_object = rcv(pclass, i)
        parameters_map[pclass].append(par_or_object)
    lastpar_id = i

    preconditions = [ ]
    effects = [ ]
    effect_preds = set()

    for i in range(random.randint(MIN_ACTION_PREDICATES, MAX_ACTION_PREDICATES)):
        pdec = random.choice(precondition_decl)

        par1_class = pdec.p1class
        par2_class = pdec.p2class
        if not parameters_map[par1_class]:
            lastpar_id += 1
            parameters_map[par1_class].append(rcv(par1_class, lastpar_id))
        if not parameters_map[par2_class]:
            lastpar_id += 1
            parameters_map[par2_class].append(rcv(par2_class, lastpar_id))

        if random.randint(0, 5):
            par1_name = random.choice(parameters_map[par1_class])
        else:
            par1_name = random.choice(objects_dict[par1_class])

        if random.randint(0, 5):
            par2_name = random.choice(parameters_map[par2_class])
        else:
            par2_name = random.choice(objects_dict[par2_class])

        objects_used.add(par1_name)
        objects_used.add(par2_name)
        
        pred = f"({pdec.pname} {par1_name} {par2_name})"

        if random.randint(0, 4):
            preconditions.append(pred)
        else:
            if random.randint(0, 5):
                effects.append(pred)
                effect_preds.add(pdec)
            else:
                effects.append(f"(not {pred})")


    seffects = '\n                '.join(set(effects))
    spre = '\n                '.join(set(preconditions))

    parameters = gen_parameters(list(objects_used))

    if len(effects) and len(preconditions):
        return f"""
        (:action random-action-{random.randint(0,1000000)}
            :parameters ({parameters})
            :precondition (and
                {spre}
            )
            :effect (and
                {seffects}
            )
        )
        """, effect_preds
    return "", effect_preds


def gen_full_domain():
    object_counter = 0

    objects_dict = collections.defaultdict(list)

    class_id = 0
    for i in range(random.randint(MIN_CLASSES, MAX_CLASSES)):
        class_id += 1
        r_classname = f"rpclass{class_id}"
        objects_dict[r_classname] = []
        for j in range(random.randint(MIN_OBJECTS_PERCLASS, MAX_OBJECTS_PERCLASS)):
            object_counter += 1
            objname = f"rpobj{object_counter}"
            objects_dict[r_classname].append(objname)
    
    precondition_decl = gen_random_predicates_defs(list(objects_dict.keys()))
    actions = []

    all_effpreds = set()

    for i in range(random.randint(MIN_ACTIONS, MAX_ACTIONS)):
        act, effpreds = gen_random_action(list(objects_dict.keys()), objects_dict, precondition_decl)
        all_effpreds |= effpreds
        actions.append(act)

    predicates = [str(p) for p in precondition_decl]

    sact = '\n    '.join(actions)
    spredicates = '\n        '.join(predicates)

    types_tax = " ".join(objects_dict.keys()) + " - object"

    assert len("".join(actions)), "No actions generated"

    return f"""(define (domain random)
    (:requirements :strips :typing :equality :negative-preconditions :disjunctive-preconditions)
    (:types {types_tax})
    (:predicates 
        {spredicates}
    )
        {sact}
)
    """, precondition_decl, objects_dict, all_effpreds


def gen_full_problem():

    domain_str, precondition_decl, objects_dict, all_effpreds = gen_full_domain()

    init_facts = [ ]
    for i in range(random.randint(2,5)):
        pdecl = random.choice(precondition_decl)
        init_facts.append(f"({pdecl.pname} {random.choice(objects_dict[pdecl.p1class])} {random.choice(objects_dict[pdecl.p2class])})")

    goals = [ ]
    for i in range(random.randint(1,2)):
        assert all_effpreds, "Can't go without any effects"
        pdecl = random.choice(list(all_effpreds))
        goals.append(f"({pdecl.pname} {random.choice(objects_dict[pdecl.p1class])} {random.choice(objects_dict[pdecl.p2class])})")

    random.shuffle(goals)
    random.shuffle(init_facts)

    for g in goals:
        assert not g in init_facts, "Problem goal already reached"

    sfacts = '\n        '.join(set(init_facts))
    sgoals = '\n            '.join(set(goals))

    objects_definition = []


    for classname, objl in objects_dict.items():
        objects_definition.append(f"{' '.join(list(objl))} - {classname}")

    random.shuffle(objects_definition)

    return domain_str, f"""(define (problem random)
    (:domain random)
    (:objects 
        {' '.join(objects_definition)}
    )
    (:init
        {sfacts}
    )
    (:goal
        (and
            {sgoals}
        )
    )
)
"""

def solve_problem(domfn, probfn, sfx="", planlen=3, fldr=""):
    solve_str = f"fast-downward --plan-file {fldr}/out{sfx}.plan --sas-file {fldr}/output{sfx}.sas {domfn} {probfn} --translate-options --total-queue-pushes 50000000000 --search-options --evaluator 'hff=ff()' --evaluator 'hlm=lmcount(lm_rhw(reasonable_orders=true),transform=no_transform())' --search 'lazy(alt([single(hff),single(hff,pref_only=true),single(hlm),single(hlm,pref_only=true),type_based([hff,g()])],boost=1000), preferred=[hff,hlm], cost_type=one, reopen_closed=false, randomize_successors=true, preferred_successors_first=false, bound=infinity)'"
    p = subprocess.run(solve_str, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    if p.returncode == 0:
        if len(open(f"{fldr}/out{sfx}.plan").readlines()) < planlen: return 1000
    return p.returncode

if __name__ == "__main__":
    cur_cnt = 0
    max_cnt = int(sys.argv[1])
    planlen = int(sys.argv[2])    # minimum length of a plan 
    sfx = sys.argv[3]             # suffix to run with
    problem_folder = sys.argv[4]  # output folder
    if len(sys.argv) == 6:
        # means randomize everything
        maxrnd = int(sys.argv[5])
        MAX_ACTION_PARAMS = maxrnd
        MAX_ACTION_PREDICATES = maxrnd
        MAX_ACTIONS = maxrnd
        MAX_CLASSES = maxrnd
        MAX_OBJECTS_PERCLASS = maxrnd

    attempts = 0
    # sfx = "_"+str(random.randint(1000000, 9999999999999))
    # sfx = ""
    while cur_cnt < max_cnt:
        pred_id = 0
        i = cur_cnt
        # dfn = f'./domain_{i}{sfx}.pddl'
        # pfn = f'./problem_{i}{sfx}.pddl'
        dfn = problem_folder+f'/domain_{sfx}.pddl'
        pfn = problem_folder+f'/problem_{sfx}.pddl'
        try:
            dom, prob = gen_full_problem()
        except AssertionError:
            attempts += 1
            continue
        # print("Past assert")
        sys.stdout.flush()

        open(dfn, 'w+').write(dom)
        open(pfn, 'w+').write(prob)
        if solve_problem(dfn, pfn, sfx, planlen, problem_folder) == 0:
            print("OK", attempts)
            cur_cnt += 1
            attempts = 0
        else:
            attempts += 1

