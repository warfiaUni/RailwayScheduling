limit(7).

% (agentID,start,target,starting-orientation,earliest-departure)
schedule(0,(1, 2),(1, 0),1,0).
schedule(1,(1, 0),(1, 2),3,0).

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
