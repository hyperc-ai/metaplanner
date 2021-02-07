import random
import sys
# Generate "apples" simple problem variations


# Predicates are ignored by metaplanner
predicates = """
        (apple-is-on ?apple-0 - obj ?tree-1 - obj)
        (hand-has ?hand-0 - obj ?apple-1 - obj)
        (is-at ?me-0 - obj ?tree-1 - obj)
"""

def rcv(name):
    "Generate a random var-obj"
    return random.choice([name, f"?{name}-{random.randint(1,5)}"])

def gen_take_apple_action():
    """ Generate a working take apple action """

    apple = random.choice(["apple", "?apple-0"])
    apple2 = random.choice(["apple", "?apple-0"])
    me = random.choice(["me", "?me-2"])
    me2 = random.choice(["me", "?me-2"])
    tree = random.choice(["tree", "?tree"])
    tree1 = random.choice(["tree", "?tree"])
    tree2 = random.choice(["tree", "?tree"])
    hand = random.choice(["hand", "?hand"])

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

    take_apple_action = f"""
    (:action take-apple 
        :parameters (ignored)
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

    apple = rcv("apple")
    tree1 = rcv("tree")

    random_preconditions = [
       f"(apple-is-on {apple} {tree})",
       f"(is-at {me} {tree1})"
    ]

    for i in range(random.randint(0,2)):
        preconditions.append(random.choice(random_preconditions))

    effects = [
        f"(is-at {me} {tree})"
    ]

    random.shuffle(preconditions)
    random.shuffle(effects)

    seffects = '\n            '.join(effects)
    spre = '\n            '.join(preconditions)

    return f"""
    (:action move_to_tree
        :parameters (ignored)
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
    (:types obj - object)
    (:predicates 
            {predicates}
        )
        {sact}
)
    """



def gen_full_problem():

    objects = ["me" "apple", "hand", "tree"]
    for i in range(random.randint(0,2)):
        objects.append(f"obj{i}")

    random.shuffle(objects)

    init_facts = [
        "(apple-is-on apple tree)",
        "(is-at me home)"
    ]

    for i in range(random.randint(0,2)):
        init_facts.append(f"({random.choice(['apple-is-on', 'hand-has', 'is-at'])} f{random.choice(objects)} f{random.choice(objects)})")

    goals = [
        "(hand-has hand apple)",
        "(is-at me tree)"
    ]

    random.shuffle(goals)
    random.shuffle(init_facts)

    sfacts = '\n        '.join(init_facts)
    sgoals = '\n            '.join(goals)


    return f"""
(define (problem apples1)
    (:domain apples1)
    (:objects 
        {' '.join(objects)} - obj
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

if __name__ == "__main__":
    for i in range(int(sys.argv[1])):
        open(f'./domain_{i}.pddl', 'w+').write(gen_full_domain())
        open(f'./problem_{i}.pddl', 'w+').write(gen_full_problem())

