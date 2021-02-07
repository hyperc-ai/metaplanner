import random
import sys
import collections
import subprocess
# Generate "apples" simple problem variations


# Predicates are ignored by metaplanner
predicates = """
        (apple-is-on ?apple-0 - oapple ?tree-1 - otree)
        (hand-has ?hand-0 - ohand ?apple-1 - oapple)
        (is-at ?me-0 - ome ?tree-1 - otree)
"""

def rcv(name, idx=0):
    "Generate a random var-obj"
    if idx == 0:
        return random.choice([name, f"?{name}-{random.randint(1,5)}"])
    else:
        return random.choice([name, f"?{name}-{idx}"])


def gen_parameters(l_objects):
    parameters = []
    for obj in l_objects:
        if obj.startswith("?"):
            classname = "o"+obj[1:].split("-")[0]
            parameters.append(f"{obj} - {classname}")
    return " ".join(parameters)


def gen_take_apple_action():
    """ Generate a working take apple action """

    apple = random.choice(["apple", "?apple-0"])
    apple2 = random.choice(["apple", "?apple-0"])
    me = random.choice(["me", "?me-2"])
    me2 = random.choice(["me", "?me-2"])
    tree = random.choice(["tree", "?tree-0"])
    tree1 = random.choice(["tree", "?tree-0"])
    tree2 = random.choice(["tree", "?tree-0"])
    hand = random.choice(["hand", "?hand-1"])

    preconditions = [
       f"(apple-is-on {apple} {tree})",
       f"(is-at {me} {tree1})"
    ]

    effects = [
            f"(hand-has {hand} {apple2})",
            f"(not (is-at {me2} {tree2}))"
    ]

    random.shuffle(preconditions)
    random.shuffle(effects)
    
    seffects = '\n            '.join(effects)
    spre = '\n            '.join(preconditions)

    parameters = gen_parameters(set([apple, apple2, me, me2, tree, tree1, tree2, hand]))

    take_apple_action = f"""
    (:action take-apple-{random.randint(0,1000000)} 
        :parameters ({parameters})
        :precondition (and
            {spre}
        )
        :effect (and
            {seffects}
        )
    )
    """
    return take_apple_action

def gen_move_to_tree():
    "Generate working action"

    me = rcv("me")
    home = rcv("home")
    tree = rcv("tree")

    preconditions = [
        f"(is-at {me} {home})"
    ]

    objects_used = set([me, home, tree])

    apple = rcv("apple")
    tree1 = rcv("tree")

    random_preconditions = [
       f"(apple-is-on {apple} {tree})",
       f"(is-at {me} {tree1})"
    ]

    for i in range(random.randint(0,2)):
        d = random.choice(random_preconditions)
        if "apple" in d:
            objects_used.add(apple)
        if "is-at" in d:
            objects_used.add(tree1)
        preconditions.append(d)

    effects = [
        f"(is-at {me} {tree})"
    ]

    random.shuffle(preconditions)
    random.shuffle(effects)

    seffects = '\n            '.join(effects)
    spre = '\n            '.join(preconditions)

    parameters = gen_parameters(list(objects_used))

    return f"""
    (:action move_to_tree_{random.randint(0,1000000)}
        :parameters ({parameters})
        :precondition (and
            {spre}
        )
        :effect (and
            {seffects}
        )
    )
    """

def gen_full_domain():
    actions = [gen_take_apple_action(), gen_move_to_tree()]

    for i in range(random.randint(0, 1)):
        actions.append(random.choice([gen_take_apple_action(), gen_move_to_tree()]))

    random.shuffle(actions)

    sact = '\n    '.join(actions)

    return f"""
(define (domain apples1)
    (:requirements :strips :typing :equality :negative-preconditions :disjunctive-preconditions)
    (:types ome otree ohand oapple ohome - object)
    (:predicates 
            {predicates}
        )
        {sact}
)
    """


def clsname_from_obj(obj):
    assert not obj.startswith("?")
    assert not "-" in obj
    classname = "o"+obj
    return classname


def gen_full_problem():

    objects_list = ["me", "apple", "hand", "tree", "home"]
    objects = collections.defaultdict(set)
    classnames = [clsname_from_obj(x) for x in objects_list]
    for obj, cls_ in zip(objects_list, classnames):
        objects[cls_].add(obj)

    for i in range(random.randint(0,2)):
        rclass = random.choice(classnames)
        objects[rclass].add(f"obj{i}")


    init_facts = [
        "(apple-is-on apple tree)",
        "(is-at me home)"
    ]

    for i in range(random.randint(0,2)):
        init_facts.append(f"({random.choice(['apple-is-on', 'hand-has', 'is-at'])} {random.choice(objects_list)} {random.choice(objects_list)})")

    goals = [
        "(hand-has hand apple)",
        "(is-at me tree)"
    ]

    random.shuffle(goals)
    random.shuffle(init_facts)

    sfacts = '\n        '.join(init_facts)
    sgoals = '\n            '.join(goals)

    objects_definition = []


    for classname, objl in objects.items():
        objects_definition.append(f"{' '.join(list(objl))} - {classname}")

    random.shuffle(objects_definition)

    return f"""
(define (problem apples1)
    (:domain apples1)
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

def solve_problem(domfn, probfn):
    solve_str = f"fast-downward --plan-file ./out.plan --sas-file ./output.sas {domfn} {probfn} --translate-options --total-queue-pushes 50000000000 --search-options --evaluator 'hff=ff()' --evaluator 'hlm=lmcount(lm_rhw(reasonable_orders=true),transform=no_transform())' --search 'lazy(alt([single(hff),single(hff,pref_only=true),single(hlm),single(hlm,pref_only=true),type_based([hff,g()])],boost=1000), preferred=[hff,hlm], cost_type=one, reopen_closed=false, randomize_successors=true, preferred_successors_first=false, bound=infinity)'"
    p = subprocess.run(solve_str, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    return p.returncode

if __name__ == "__main__":
    cur_cnt = 0
    max_cnt = int(sys.argv[1])
    attempts = 0
    while cur_cnt < max_cnt:
        i = cur_cnt
        dfn = f'./domain_{i}.pddl'
        pfn = f'./problem_{i}.pddl'
        open(dfn, 'w+').write(gen_full_domain())
        open(pfn, 'w+').write(gen_full_problem())
        if solve_problem(dfn, pfn) == 0:
            print("OK", attempts)
            cur_cnt += 1
            attempts = 0
        else:
            attempts += 1

