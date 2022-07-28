PROG    START   0
.       test program for immediate and indirect addressing
FIRST   LDA     #100
        STA     ALPHA
        LDA     @BETA
        ADD     #50
        STA     GAMMA
        LDCH    DATA,X
        RSUB
ALPHA   RESW    1
BETA    WORD    100
GAMMA   RESW    1
DATA    BYTE    C'HELLO'
        END     FIRST
