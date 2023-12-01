% on cell (1,0):
%cell((1,0),1,1). % a train facing east can go east
%cell((1,0),3,1). % a train facing west can go east
% on cell (1,1):
%cell((1,1),1,1). % a train facing east can go east
%cell((1,1),1,0). % a train facing east can also go north
%cell((1,1),2,3). % a train facing south can go west
%cell((1,1),3,3). % a train facing west can go west
% and so on...
%cell((1,2),3,3).
%cell((1,2),1,3).
%cell((0,1),0,1).
%cell((0,1),3,2).
%cell((0,2),3,3).
%cell((0,2),1,3).

% (start,target,starting-orientation)
schedule((1,0),(0,2),e).

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


{direction(D,T):cell((X,Y),O,D)}=1 :- limit(L), 
                                    T<L, 
                                    not done(T),
                                    trans(_,(X,Y),O,T).

trans((X,Y),(X+A,Y+B),D,T+1) :- trans(_,(X,Y),_,T), direction(D,T), diff(D,A,B). 

%TODO: timestep already in trans
1{trans((X,Y),(X+A,Y+B),O,0):diff(D,A,B)}1 :- cell((X,Y),O,D), schedule((X,Y),(_,_),O).

% create path to possible next cell from each cell regarding train [O]rientation
%{trans((X,Y),(X+A,Y+B),O,T+1):diff(D,A,B)} = 1 :-   cell((X,Y),O,D), 
%                                                    limit(L), 
%                                                    T<L, 
%                                                    not done, 
%                                                    trans(_,(X,Y),O,T).

%:-trans(_,(X,Y),_,T), trans(_,(X',Y'),_,T), (X-X')**2+(Y-Y')**2!=0.

% define begin of solution
%sln((X,Y),(X2,Y2),0,O) :- schedule((X,Y),(_,_),O), trans((X,Y),(X2,Y2),O).

% continue solution path sln((X,Y),(X2,Y2),[T]imestep, train [O]rientation) until target is reached (M,N)
%sln((X,Y),(X2,Y2),T+1,NEWO) :- trans((X,Y),(X2,Y2),O), sln((_,_),(X,Y),T,O), schedule((_,_),(M,N),_), diff(NEWO,X2-X,Y2-Y), (X,Y) != (M,N), T<3.

done(T) :- schedule((_,_),(X,Y),_), trans(_,(X,Y),_,T).

%:- not done.
% Display the result
#show trans/4.
#show done/1.
%#show sln/4.








