% count number of choices in each cell and direction
count(P,O,C) :- C = #count{D:cell(P,O,D)},cell(P,O,_).

decision_point(P) :- cell(P,O,D), count(P,O,C), C>1.

% At the start choose a direction to move towards
% predict starting direction
1{pred_direction(ID,D,T):cell(P,O,D)}1 :- schedule(ID,P,_,O,T).
% predict starting transition
pred_trans(ID,(Y,X),(Y+DY,X+DX),D,T+1) :- schedule(ID,(Y,X),_,O,T), 
                                        pred_direction(ID,D,T), 
                                        diff(D,DY,DX).
%---------------------------------------------------------------
% At decision points the agent has to choose a direction as well
% predict direction
1{pred_direction(ID,D,T):cell(P,O,D)}1 :- decision_point(P),
                                         limit(L), 
                                         T<L, 
                                         not done(ID,T),
                                         trans(ID,_,P,O,T).

% predict transition
pred_trans(ID,(Y,X),(Y+DY,X+DX),D,T+1) :- trans(ID,_,(Y,X),_,T), 
                                        pred_direction(ID,D,T), 
                                        diff(D,DY,DX).
%----------------------------------------------------------------
% If the agent is not at a decition point then the 
% prediction follows directly
pred_trans(ID,(Y,X),(Y+DY,X+DX),D,T+1) :- trans(ID,_,(Y,X),O,T), 
                                          cell((Y,X),O,D), 
                                          diff(D,DY,DX),
                                          limit(L), 
                                            T<L, 
                                            not done(ID,T),
                                            not decision_point((Y,X)).


pred_coll(ID,ID',T) :- pred_trans(ID,_,P',_,T), pred_trans(ID',_,P',_,T), ID!=ID'.
pred_coll(ID,ID',T) :- pred_trans(ID,P,P',_,T), pred_trans(ID',P',P,_,T), ID!=ID'.

% if there are no colliding predictions, move
trans(ID,P,P',D,T) :- pred_trans(ID,P,P',D,T), not pred_coll(ID,_,T) .

% otherwise let agent decide between prediction and halting
1{trans(ID,P,P',D,T);trans(ID,P,P,O,T)}1 :- pred_trans(ID,P,P',D,T), 
                                            pred_coll(ID,_,T),
                                            trans(ID,_,P,O,T-1).

% otherwise let agent decide between prediction and halting
1{trans(ID,P,P',D,T);trans(ID,P,P,O,T)}1 :- pred_trans(ID,P,P',D,T), 
                                            pred_coll(ID,_,T),
                                            schedule(ID,P,_,O,T-1).

% reached target?
done(ID,T) :- schedule(ID,_,P,_,_), trans(ID,_,P,_,T).

% transform transitions into actions
%left=1,forward=2,right=3,wait=4
agent_action(ID, 4,T):- trans(ID,A,A,_,T).
agent_action(ID, 2,T):- trans(ID,A,B,_,T), trans(ID,_,A,O,T-1), A!=B, count(A,O,1).
agent_action(ID, 2,T):- trans(ID,A,B,_,T), schedule(ID,A,_,O,T), A!=B, count(A,O,1).
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



%collision constraints:
:- trans(ID,_,P',_,T), trans(ID',_,P',_,T), ID!=ID'. %no two on one field
:- trans(ID,P,P',_,T), trans(ID',P',P,_,T), ID!=ID'. % no two past each other

:- not done(ID,_), schedule(ID,_,_,_,_).

% count number of choices in each cell and direction
count(A,O,C) :- C = #count{D:cell(A,O,D)},cell(A,O,_).




#show schedule/5.
#show pred_direction/3.
#show pred_trans/5.
#show trans/5.
#show pred_coll/3.
#show done/2.
#show agent_action/3.
