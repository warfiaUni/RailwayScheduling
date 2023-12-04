limit(5).

% (agentID,start,target,starting-orientation)
schedule(0,(1, 0),(0, 2),1,0).
schedule(1,(1, 2),(1, 0),3,1).

%grid definition cell((Y,X),train orientation, (possible directions))
cell((0,1),0,(1)).
cell((0,1),3,(2)).
cell((0,2),3,(3)).
cell((0,2),1,(3)).
cell((1,0),1,(1)).
cell((1,0),3,(1)).
cell((1,1),1,(0;1)).
cell((1,1),2,(3)).
cell((1,1),3,(3)).
cell((1,2),3,(3)).
cell((1,2),1,(3)).

% define differences to calculate adjacent cells
diff(0, -1, 0). % North
diff(1, 0, 1).  % East
diff(2, 1, 0).  % South
diff(3, 0, -1). % West

%TODO: waiting in station

% start path
1{trans(ID,(X,Y),(X+A,Y+B),O,T):diff(D,A,B),cell((X,Y),O,D)}1 :-  
                                            schedule(ID,(X,Y),_,O,T).

% choose direction
{direction(ID,D,T):cell((X,Y),O,D)}1 :- limit(L), 
                                    T<L, 
                                    not done(ID,T),
                                    trans(ID,_,(X,Y),O,T). 

% continue path
trans(ID,(X,Y),(X+A,Y+B),D,T+1) :- trans(ID,_,(X,Y),_,T), 
                                direction(ID,D,T), 
                                diff(D,A,B).

% continue path when action is waiting
trans(ID,(X,Y),(X,Y),O,T+1) :- trans(ID,_,(X,Y),O,T), 
                                not direction(ID,_,T),
                                limit(L), 
                                T<L,
                                not done(ID,T).

% reached target?
done(ID,T) :- schedule(ID,_,(X,Y),_,_), trans(ID,_,(X,Y),_,T).

%collision constraints:
:- trans(ID,_,B,_,T), trans(ID',_,B,_,T), ID!=ID'. %no two on one field
:- trans(ID,A,B,_,T), trans(ID',B,A,_,T), ID!=ID'. % no two past each other

% Display the result
#show trans/5.
#show fl_action/3.

%turn into flatland actions
%TODO: no_op=0,left=1,forward=2,right=3,wait=4
fl_action(ID,1,T) :- trans(ID,_,_,OLD,T),trans(ID,_,_,NEW,T+1), NEW == (OLD+3)\4, not fl_action(ID,4,T). %left
fl_action(ID,2,T) :- trans(ID,_,_,OLD,T),trans(ID,_,_,NEW,T+1), NEW == OLD, not fl_action(ID,4,T).
fl_action(ID,3,T) :- trans(ID,_,_,OLD,T),trans(ID,_,_,NEW,T+1), NEW == (OLD+1)\4, not fl_action(ID,4,T). %right
fl_action(ID,4,T) :- trans(ID,A,B,_,T), A==B.