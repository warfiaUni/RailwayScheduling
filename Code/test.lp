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
cell((1,1),e,(n;e)).
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

t(32).

%TODO: timestep already in trans

% create path to possible next cell from each cell regarding train [O]rientation
1{trans((X,Y),(X+A,Y+B),O):diff(D,A,B)}1 :- cell((X,Y),O,D).

% define begin of solution
sln((X,Y),(X2,Y2),0,O) :- schedule((X,Y),(_,_),O), trans((X,Y),(X2,Y2),O).

% continue solution path sln((X,Y),(X2,Y2),[T]imestep, train [O]rientation) until target is reached (M,N)
sln((X,Y),(X2,Y2),T+1,NEWO) :- trans((X,Y),(X2,Y2),O), sln((_,_),(X,Y),T,O), schedule((_,_),(M,N),_), diff(NEWO,X2-X,Y2-Y), (X,Y) != (M,N), T<3.

% Display the result
%#show trans/3.
#show sln/4.








