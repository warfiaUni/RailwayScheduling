% (agentID, start,target,starting-orientation, departure-time)
schedule(0,(1,0),(0,2),e,0).
%schedule(1,(1,2),(1,0),w,0).



%grid definition cell((Y,X),train orientation, (possible directions))
cell((0,1),n,(e;m)).
cell((0,1),w,(s;m)).
cell((0,2),e,(w;m)).
cell((1,0),e,(e;m)).
cell((1,0),w,(e;m)).
cell((1,1),e,(n;e;m)).
cell((1,1),s,(w;m)).
cell((1,1),w,(w;m)).
cell((1,2),e,(w;m)).
cell((1,2),w,(w;m)).



%cell((1,3),w,(w)).
%cell((1,3),e,(w)).

% define differences to calculate adjacent cells
diff(n, -1, 0). % North
diff(e, 0, 1).  % East
diff(s, 1, 0).  % South
diff(w, 0, -1). % West
diff(m,0,0). %wait

limit(10).

%TODO: change waiting into (not direction and {}1)
%idea: waiting only before switch?
%TODO: no_op=1,left=1,forward=2,right=3,wait=4 

% start path
1{trans(ID,(X,Y),(X+A,Y+B),O,T):diff(D,A,B),cell((X,Y),O,D)}1 :-  
                                            schedule(ID,(X,Y),_,O,T).

% choose direction
{direction(ID,D,T):cell((X,Y),O,D)}=1 :- limit(L), 
                                    T<L, 
                                    not done(ID,T),
                                    trans(ID,_,(X,Y),O,T). 

% continue path
trans(ID,(X,Y),(X+A,Y+B),D,T+1) :- trans(ID,_,(X,Y),_,T), 
                                direction(ID,D,T), 
                                diff(D,A,B),
                                D != m.

% continue path when action is waiting
trans(ID,(X,Y),(X+A,Y+B),O,T+1) :- trans(ID,_,(X,Y),O,T), 
                                direction(ID,D,T), 
                                diff(D,A,B),
                                D == m. % if wait take previous O

% reached target?
done(ID,T) :- schedule(ID,_,(X,Y),_,_), trans(ID,_,(X,Y),_,T).

%collision constraints:
:- trans(ID,_,B,_,T), trans(ID',_,B,_,T), ID!=ID'. %no two on one field
:- trans(ID,A,B,_,T), trans(ID',B,A,_,T), ID!=ID'. % no two past each other

% Display the result
#show trans/5.
#show done/2.
#show direction/3.