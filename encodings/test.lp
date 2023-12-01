% (start,target,starting-orientation, agentID)
schedule((1,0),(0,2),e,0).
%schedule((1,2),(1,0),w,1).

%grid definition cell((Y,X),train orientation, (possible directions))
cell((1,0),e,(e)).
cell((1,1),e,(n)).
cell((1,1),e,(e)).
cell((0,1),n,(e)).
cell((0,2),e,(w)).
cell((1,2),e,(w)).

cell((1,0),w,(e)).
cell((1,1),s,(w)).
cell((1,1),w,(w)).
cell((0,1),w,(s)).

% define differences to calculate adjacent cells
diff(n, -1, 0). % North
diff(e, 0, 1).  % East
diff(s, 1, 0).  % South
diff(w, 0, -1). % West

limit(10).

%TODO: stop when goal is reached
%TODO: multi agent: agent id rein, alles anpassen
%TODO collision constraints
%TODO: implement waiting

% choose direction
{direction(D,T):cell((X,Y),O,D)}=1 :- limit(L), 
                                    T<L, 
                                    not done(T),
                                    trans(_,(X,Y),O,T). 

% start path
1{trans((X,Y),(X+A,Y+B),O,0):diff(D,A,B)}1 :- cell((X,Y),O,D), 
                                            schedule((X,Y),(_,_),O,_).

% continue path
trans((X,Y),(X+A,Y+B),D,T+1) :- trans(_,(X,Y),_,T), 
                                direction(D,T), 
                                diff(D,A,B).

done(T) :- schedule((_,_),(X,Y),_,_), trans(_,(X,Y),_,T).

% Display the result
#show trans/4.
#show done/1.
%#show sln/4.








