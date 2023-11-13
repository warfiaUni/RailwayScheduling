% description
cell(0,0,1,1). %normal rail
cell(0,1,1,1). %normal rail
cell(0,2,1,1). %normal rail

station(0,0).
station(0,2).

schedule(1,0,0,0,2). % train 1 from (0,0) to (0,2)

% to where can a train go (diff for horizontal rail)
% case 1: straight horizontal rail
transition(1,0,1). % (case no, diff X, diff Y)
transition(1,0,-1).

% create possible paths from each cell
{path(X,Y,X+A,Y+B):transition(T,A,B)}1 :- cell(X,Y,T,_).

sorted(X,Y,X2,Y2,0):-path(X,Y,X2,Y2),schedule(_,X,Y,_,_). %define starting point path sorted(X,Y,X2,Y2,time step)

% continue path
sorted(X,Y,X2,Y2,M2):-sorted(_,_,X,Y,M),path(X,Y,X2,Y2),M2=M+1,M<5. %TODO: stop when destination is reached instead of M<5

% find path that contains both stations /or exclude paths that dont have stations
:- 0{sorted(X,Y,X2,Y2,M)}1. 
:- schedule(_,X,Y,X2,Y2), not sorted(X,Y,_,_,_). % exclude every path that is not scheduled
:- schedule(_,X,Y,X2,Y2), not sorted(_,_,X2,Y2,_). 

% stop when destination is reached
:- sorted(X,Y,_,_,_), schedule(_,_,_,X,Y).


#show sorted/5.