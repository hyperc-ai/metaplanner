(define (problem maze1)
    (:domain maze1)
    (:objects 
        agent - agent n1 n2 n3 n4 - node
    )
    (:init
        (is-at agent n2)
        (node-connected n1 n2)
        (node-connected n2 n1)
        (node-connected n2 n3)
        (node-connected n3 n4)
    )
    (:goal
        (and
            (is-at agent n4)
        )
    )
)

