%Facts q(42).
%Rules p(X):- q(X), not r(X).
%Conditional Literals p:-q(X):r(X).
%Disjunction p(X); q(X):-r(X).
%Integraty Constraints :- q(X), p(X).
%Choice 2{p(X,Y): q(X)}7:-r(Y).
%Aggregates s(Y):- r(Y), 2#sum{X: p(X,Y), q(X)} 7.
%Multi-objective optimization :~ q(X), p(X, C). [C@42]
%#minimize { C@42: q(X), p(X,C)}  ==> (WIESO IST HIER KEIN PUNKT UND NIX?) Sieht unvollständig aus.


% Legende Typetransitions: https://flatland.aicrowd.com/getting-started/env.html
% case 0: "empty"
% case 1: "straight" North-South (0) // East-West (1)
% case 2: "simple switch" North-South XOR West-South // 4 rotations possible?
% case 3: "Diamond crossing" North-South XOR West-East
% case 4: "single slip switch" Case 3+2
% case 5: "double slip switch" Case 3+North-West XOR South-East
% case 6: "symmetrical switch" South-West XOR South-East
% case 7: "dead-end" South-North-Stop 

%Furthermore:we shall rotate all of them (22 or 23 cases if we stupidly make a list) ==> Which case was needed to mirror?
%
%
%
%
%
% ...
%
%
%
%
%
%
% shall we A:continue this list XOR  B: shall by calling them 1.1., 1.2., 1.3. including (Transitiontype.Orientation) XOR C:shall we add rotation as extra variable (x,y,tt,rotation) 
% erstmal an Mariekes Code halten, damit dann auch die instances mit dem Python Code klappt?


% description cell(x,y,typtransition, orientation(hier vllt objektiv oder subj)) => siehe PNG, ist es hinderlich, das PNG unten links (0,0) hat, oder irrelevant?
cell(0,0,1,0). %case 1 "straight" with orientation: 1 *Objectively speaking*
cell(0,1,2,1). %case 2 "simple switch" with orientation: 1 
cell(0,2,7,1). %case 7 "Dead End" with orientation: 1
cell(1,0,0,0). %case 0 "empty cell" (gar nicht benennnen?)
cell(1,1,0,0). %case 0 "empty cell" => ACHTUNG: eigentlich hier 90° Kurve aber taucht als CASE gar nicht auf? 
cell(1,2,7,1). %case 7 "Dead End" with orientation: 1

station(0,0).
station(0,2).

% schedulde(ID Train, X1, Y1, X2, Y2)
schedule(1,0,0,0,2). % train-ID (1) from (0,0) to (0,2) % OK!


% schedulde(ID Train, X2, Y2, X3, Y3) 
% =====================================> Muss hier noch was hin?


% to where can a train go? (up, right, down, left) 
transition(1,0,0,1). %"UP" %(Train-ID, diff X, diff Y) => hier wäre eine Variable mehr benötigt für transition(case, orientation, X, Y)
transition(1,0,0,-1). %"DOWN" 
transition(1,1,1,0). %"RIGHT"
transition(1,1,-1,0). %"LEFT"
% ======================================> muss man hier alle transitions für alle cases mit allen orientations aufzählen? Oder wie war das initial gedacht?


% create possible paths from each cell. CHOICE: choose from { ... } exactly 1 :- so that there is a cell(X,Y,T,_).
{path(X,Y,X+A,Y+B):transition(T,O,A,B)}1 :- cell(X,Y,T,_). 
%=======================================> Warum hier cell (X,Y,T,_)? Vorschlag: cell(X,Y,T,O)? @Marieke: warum das O = _ ?


sorted(X,Y,X2,Y2,0):-path(X,Y,X2,Y2),schedule(_,X,Y,_,_). %define starting point path sorted(X,Y,X2,Y2,time step)
%=======================================> Verstehe den Begriff "sorted" hier noch nicht 


% continue path
sorted(X,Y,X2,Y2,M2):-sorted(_,_,X,Y,M),path(X,Y,X2,Y2),M2=M+1,M<5. %TODO: stop whedn destination is reached instead of M<5 
%=======================================> Momentan künstliche Begrenzung Timesteps, aber wir brauchen Timesteps XOR Train-ID arrives at Goal.

% find path that contains both stations /or exclude paths that dont have stations
:- 0{sorted(X,Y,X2,Y2,M)}1. %mind. 0 oder 1 Pfad finden?
:- schedule(_,X,Y,X2,Y2), not sorted(X,Y,_,_,_). % exclude every path that is not scheduled, kann man das "not" so anwenden?
:- schedule(_,X,Y,X2,Y2), not sorted(_,_,X2,Y2,_). 
%=======================================> 

% stop when destination is reached
:- sorted(X,Y,_,_,_), schedule(_,_,_,X,Y). 
%=======================================>%It is not the case, that there is a sorted(X,Y,,,), (and) schedulde(,,,X,Y)?
