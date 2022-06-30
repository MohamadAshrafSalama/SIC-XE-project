SUM     START   0
.       program to compute sum of N values
        LDA     N
        STA     COUNT
        LDX     #0
        LDA     #0
LOOP    ADD     TABLE,X
        TIX     COUNT
        JLT     LOOP
        STA     TOTAL
        RSUB
N       WORD    5
TABLE   WORD    10
        WORD    20
        WORD    30
        WORD    40
        WORD    50
COUNT   RESW    1
TOTAL   RESW    1
        END     SUM
