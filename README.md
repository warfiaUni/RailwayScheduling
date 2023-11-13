# RailwayScheduling
Attempt at solving the [Flatland Challenge](https://flatland.aicrowd.com/intro.html) with ASP.

## Fact Format for Environment Generation
### Grid
```
cell((Y,X),O,D)
(Y,X) - position of cell
O     - orientation of possible train
D     - possible direction the train can move from its orientation
```
### Schedule
```
schedule((start),(target),departure,agentID)
start - (Y,X) initial position of agent
target - (Y,X) target of agent
departure - time step at which train is allowed to depart
agentID
```
