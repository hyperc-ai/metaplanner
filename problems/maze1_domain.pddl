(define (domain maze1)
    (:requirements :strips :typing :equality :negative-preconditions :disjunctive-preconditions)
    (:types agent node - object)
    (:predicates 
        (is-at ?v1 - agent ?v2 - node)
        (node-connected ?n1 - node ?n2 - node)
    )

    (:action move-to-next-node-first-2
        :parameters (?agent - agent ?node-1 - node ?node-2 - node)
        :precondition (and
            (is-at ?agent ?node-1)
            (node-connected ?node-1 ?node-2)
        )
        :effect (and
            (is-at ?agent ?node-2)
        )
    )

    (:action move-to-next-node-first
        :parameters (?agent - agent ?node-1 - node ?node-2 - node)
        :precondition (and
            (is-at ?agent ?node-1)
            (node-connected ?node-1 ?node-2)
        )
        :effect (and
            (is-at ?agent ?node-2)
        )
    )

)
