% These are the rules that are used to infer relationships between the various protagonist
% of a book. The following rules are essentially about family relationships but can be modeled
% to fit any expert need

:- use_module(library(tabling)).
:- table status/2.
:- table related/3.
:- discontiguous related/2.
:- discontiguous status/3.

status(X,female):-related(X,_,daughter).
status(X,female):-related(X,_,mother).
status(X,female):-related(X,_,sister).
status(X,female):-related(X,_,wife).
status(X,female):-related(_,X,husband).
status(X,female):-related(X,_,grandmother).
status(X,female):-related(X,_,grandmother).
status(X,female):-related(X,_,sister_in_law).

status(X,male):-related(X,_,brother).
status(X,male):-related(X,_,father).
status(X,male):-related(X,_,husband).
status(X,male):-related(_,X,wife).
status(X,male):-related(X,_,son).
status(X,male):-related(X,_,brother_in_law).
status(X,male):-related(X,_,grandfather).
status(X,male):-related(X,_,grandfather).

related(X,Y,brother):-related(X,Y,siblings),status(X,male).

related(X,Y,child):-related(X,Y,daughter).
related(X,Y,child):-related(Y,X,parent).
related(X,Y,child):-related(X,Y,son).

related(X,Y,daughter):-related(X,Y,child),status(X,female).

related(X,Y,father):-related(Mother,Y,mother),related(X,Mother,husband).
related(X,Y,father):-related(X,Y,parent),status(X,male).

related(X,Y,husband):-related(X,Y,married),status(X,male).

related(X,Y,married):-related(X,Y,husband).
related(X,Y,married):-related(Y,X,married).
related(X,Y,married):-related(X,Y,wife).
related(X,Y,married):-related(X,Z,parent),related(Y,Z,parent),X\=Y.

related(X,Y,mother):-related(Father,Y,father),related(X,Father,wife).
related(X,Y,mother):-related(X,Y,parent),status(X,female).

related(X,Y,parent):-related(X,Y,father).
related(X,Y,parent):-related(X,Y,mother).
related(X,Y,parent):-related(Y,X,child).
related(X,Y,parent):-related(X,Z,parent),related(Z,Y,siblings).

related(X,Y,siblings):-related(X,Y,brother).
related(X,Y,siblings):-related(X,Y,sister).
related(X,Y,siblings):-related(Y,X,siblings).
related(X,Y,siblings):-related(X,Z,siblings),related(Z,Y,siblings),X\=Y.

related(X,Y,sister):-related(X,Y,siblings),status(X,female).
related(X,Y,son):-related(X,Y,child),status(X,male).

related(X,Y,wife):-related(X,Y,married),status(X,female).

related(X,Y,cousin):-related(X,Z,child),related(Z,Y,parent_siblings).

related(X,Y,grandparent):-related(X,Z,parent),related(Z,Y,parent).

related(X,Y,grandfather):-related(X,Y,grandparent),status(X,male).
related(X,Y,grandmother):-related(X,Y,grandparent),status(X,female).

related(X,Y,sibling_in_law):-related(X,Y,brother_in_law).
related(X,Y,sibling_in_law):-related(X,Y,sister_in_law).
related(X,Y,sibling_in_law):-related(X,Z,sibling_in_law),related(Z,Y,sibling_in_law).
related(X,Y,sibling_in_law):-related(Y,X,sibling_in_law).
related(X,Y,sibling_in_law):-related(Y,Z,married),related(X,Z,siblings).

related(X,Y,brother_in_law):-related(X,Y,sibling_in_law),status(X,male).
related(X,Y,sister_in_law):-related(X,Y,sibling_in_law),status(X,female).

related(X,Y,parent_siblings):-related(Z,Y,parent),related(X,Z,siblings).

related(X,Y,aunt):-related(X,Y,parent_siblings),status(X,female).
related(X,Y,uncle):-related(X,Y,parent_siblings),status(X,male).