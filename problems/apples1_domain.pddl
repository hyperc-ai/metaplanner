(define (domain apples1)
    (:requirements :strips :typing :equality :negative-preconditions :disjunctive-preconditions)
    (:types obj - object)
    (:predicates 
        (apple-is-on ?apple-0 - obj ?tree-1 - obj)
        (hand-has ?hand-0 - obj ?apple-1 - obj)
        (is-at ?me-0 - obj ?tree-1 - obj)
    )
    (:action take-apple 
        :parameters (?apple-0 - obj ?tree-1 - obj ?me-2 - obj)
        :precondition (and
            (apple-is-on ?apple-0 ?tree-1)
            (is-at ?me-2 ?tree-1)
            (not (= (?tree-1 ?me-2)))
        )
        :effect (and
            (hand-has hand ?apple-0)
            (not (is-at me tree))
        )
    )

    (:action move-to-tree
        :parameters (?me-1 - obj ?tree-1 - obj)
        :precondition (and
            (is-at ?me-1 home)
        )
        :effect (and
            (is-at ?me-1 ?tree-1)
        )
    )
)
