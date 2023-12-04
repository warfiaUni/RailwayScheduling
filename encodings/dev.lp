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


% start path
1{trans(ID,(X,Y),(X+A,Y+B),D,T):diff(D,A,B),cell((X,Y),O,D);trans(ID,(X,Y),(X,Y),O,T)}1 :-  
                                            schedule(ID,(X,Y),_,O,T).

% choose direction
1{direction(ID,D,T):cell((X,Y),O,D);trans(ID,(X,Y),(X,Y),O,T+1)}1 :- limit(L), 
                                    T<L, 
                                    not done(ID,T),
                                    trans(ID,_,(X,Y),O,T). 

% continue path
trans(ID,(X,Y),(X+A,Y+B),D,T+1) :- trans(ID,_,(X,Y),_,T), 
                                direction(ID,D,T), 
                                diff(D,A,B).

% reached target?
done(ID,T) :- schedule(ID,_,(X,Y),_,_), trans(ID,_,(X,Y),_,T).

%collision constraints:
:- trans(ID,_,B,_,T), trans(ID',_,B,_,T), ID!=ID'. %no two on one field
:- trans(ID,A,B,_,T), trans(ID',B,A,_,T), ID!=ID'. % no two past each other


% count number of choices in each cell and direction
count(A,O,C) :- C = #count{D:cell(A,O,D)},cell(A,O,_).

% transform transitions into actions
%left=1,forward=2,right=3,wait=4
agent_action(ID, 4,T):- trans(ID,A,A,_,T).
agent_action(ID, 2,T):- trans(ID,A,B,_,T), trans(ID,_,A,O,T-1), A!=B, count(A,O,1).
agent_action(ID, 2,0):- trans(ID,A,B,_,0), schedule(ID,A,_,O,0), A!=B, count(A,O,1).
agent_action(ID, 2,T):- trans(ID,A,B,O,T), trans(ID,_,A,O,T-1), A!=B, count(A,O,2).

%right
agent_action(ID, 3, T) :- trans(ID,A,B,AO,T), 
                        trans(ID,_,A,O,T-1),
                        A!=B,  
                        AO=(O+1)\4,
                        not agent_action(ID,2,T).

%left
agent_action(ID, 1, T) :- trans(ID,A,B,AO,T), 
                        trans(ID,_,A,O,T-1),
                        A!=B,  
                        AO=(O+3)\4,
                        not agent_action(ID,2,T).

%agent_action(ID, 1,T-1):- trans(ID,A,B,AO,T), 
%                            A!=B, 1 < #count{D:cell((X,Y),O,D)},
%                            cell(A,O,_), 
%                            AO=(O+1)\4.

% all schedules have to be done at some point
:- not done(ID,_), schedule(ID,_,_,_,_).



% Display the result
%#show trans/5.
%#show done/2.
%#show direction/3.
#show agent_action/3.
%#show count/3.
