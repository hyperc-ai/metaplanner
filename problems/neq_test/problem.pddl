(define (problem apples1)
    (:domain apples1)
    (:objects 
        me - ome apple - oapple hand - ohand tree - otree home - ohome
    )
    (:init
        (apple-is-on apple tree)
        (is-at me home)
    )
    (:goal
        (and
            (hand-has hand apple)
            (is-at me tree)
        )
    )
)

