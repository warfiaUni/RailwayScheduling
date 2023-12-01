% (agentID, start,target,starting-orientation)
schedule(0,(1,0),(0,2),e).
schedule(1,(1,3),(1,0),w).

%grid definition cell((Y,X),train orientation, (possible directions))
cell((1,0),e,(e)).
cell((1,1),e,(n;e)).
%cell((1,1),e,(e)).
cell((0,1),n,(e)).
cell((0,2),e,(w)).
cell((1,2),e,(w)).
cell((1,2),w,(w)).

cell((1,0),w,(e)).
cell((1,1),s,(w)).
cell((1,1),w,(w)).
cell((0,1),w,(s)).

cell((1,3),w,(w)).
cell((1,3),e,(w)).

% define differences to calculate adjacent cells
diff(n, -1, 0). % North
diff(e, 0, 1).  % East
diff(s, 1, 0).  % South
diff(w, 0, -1). % West

limit(10).

%TODO: multi agent: agent id rein, alles anpassen
%TODO collision constraints
%TODO: implement waiting

% choose direction
{direction(D,T,ID):cell((X,Y),O,D)}=1 :- limit(L), 
                                    T<L, 
                                    not done(ID,T),
                                    trans(ID,_,(X,Y),O,T). 

% start path
1{trans(ID,(X,Y),(X+A,Y+B),O,0):diff(D,A,B)}1 :- cell((X,Y),O,D), 
                                            schedule(ID,(X,Y),(_,_),O).

% continue path
trans(ID,(X,Y),(X+A,Y+B),D,T+1) :- trans(ID,_,(X,Y),_,T), 
                                direction(D,T,ID), 
                                diff(D,A,B).

% reached target?
done(ID,T) :- schedule(_,_,(X,Y),_), trans(ID,_,(X,Y),_,T).

%collision constraints:
:- trans(ID,_,B,_,T), trans(ID',_,B,_,T), ID!=ID'. %no two on one field

% Display the result
#show trans/5.
#show done/2.
%#show sln/4.