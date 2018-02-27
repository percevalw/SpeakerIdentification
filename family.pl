% Functions...

:- use_module(library(tabling)).
:- table married/2.
:- table son/2.
:- table daughter/2.
:- table child/2.
:- table female/2.
:- table parent/2.
:- table father/2.
:- table parent/2.
:- table male/1.
:- table mother/2.
:- table female/1.

son(X,Y):-child(X,Y),male(X).
child(X):-son(X,Y).

male(X):-son(X,Y).
male(X):-father(X,Y).
male(X):-husband(X,Y).

daughter(X,Y):-child(X,Y),female(X).
child(X):-daughter(X,Y).

child(X,Y):-parent(Y,X).

father(X,Y):-parent(X,Y),male(X).
father(X,Y):-mother(Mother,Y),husband(X,Mother).

mother(X,Y):-parent(X,Y),female(X).
mother(X,Y):-father(Father,Y),wife(X,Father).

parent(X,Y):-child(Y,X).
parent(X,Y):-father(X,Y).
parent(X,Y):-mother(X,Y).

husband(X,Y):-married(X,Y),male(X).
wife(X,Y):-married(X,Y),female(X).

married(X,Y):-husband(X,Y).
married(X,Y):-wife(X,Y).
married(X, Y):-married(Y, X).

female(X):-daughter(X,Y).
female(X):-mother(X,Y).
female(X):-wife(X,Y).

bro_sis(X,Y):-  mother(M1,X),mother(M2,Y),
                father(F1,X),father(F2,Y),
                (   (M1=M2),not(F1=F2);
                    (F1=F2),not(M1=M2);
                    (M1=M2),(F1=F2)),X\=Y.

brother(X,Y):-bro_sis(X,Y),male(X).

sister(X,Y):-bro_sis(X,Y),female(X).

bro_in_law(X,Y):-married(Y,Z),brother(X,Z).
bro_in_law(X,Y):-sister(Z,Y),husband(X,Z).
bro_in_law(X,Y):-married(Y,Z),sister(S,Z),husband(X,S).

sis_in_law(X,Y):-married(Y,Z),sister(X,Z).
sis_in_law(X,Y):-brother(Z,Y),wife(X,Z).
sis_in_law(X,Y):-married(Y,Z),brother(S,Z),wife(X,S).

grandparent(X,Y):-parent(X,Z),parent(Z,Y).
grandfather(X,Y):-grandparent(X,Y),male(X).
grandmother(X,Y):-grandparent(X,Y),female(X).

aunt(X,Y):-parent(Z,Y),sister(X,Z).
aunt(X,Y):-parent(Z,Y),brother(S,Z),wife(X,S).

uncle(X,Y):-parent(Z,Y),brother(X,Z).
uncle(X,Y):-parent(Z,Y),sister(S,Z),husband(X,S).

cousin(X,Y):-parent(Z,X),bro_sis(S,Z),child(Y,S),
             X\=Y,not(bro_sis(X,Y)).

deepcousin(X,Y):-(cousin(X,Y);parent(M,X),parent(N,Y),deepcousin(M,N)),
                    X\=Y,not(bro_sis(X,Y)).

cousinlist([X,Y]):-cousin(X,Y).
cousinlist([X,Y|Z]):-cousin(X,Y),cousinlist([Y|Z]),not(member(X,[Y|Z])).

father(mrbennet, lizzy).
wife(mrsbennet, mrbennet).
female(lizzy).
