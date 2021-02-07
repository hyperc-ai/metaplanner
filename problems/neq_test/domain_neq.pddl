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
            (not (= ?me-2 ?tree-1))
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
