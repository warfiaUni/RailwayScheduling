# Detailed infos to ASP Encodings
This directory lists ASP encodings.

## Fact Format for Instance Generation

In order to solve Flatland environments with Answer Set Programming, all parameters relevant for solving have to be translated into an ASP instance.

### Grid

The main structure of any Flatland environment is the grid of cells. Each cell defines its own transition rules depending on the orientation of the agent.

```
cell((Y,X),O,(D)).
    (Y,X) - position of cell
    O     - orientation of train [0..3]
    (D)   - possible directions the train can move towards [0..3]
```

<details>
<summary>Examples</summary>

```python
#cell((1,4),north,(east))
cell((1,4),0,(1)).
```

Represents the cell that is 2nd from the top and 5th from the left. The cell allows an agent that is oriented northward to only move east (turn right).

```python
#cell((3,2),east,(east;south))
cell((3,2),1,(1;2)).
```
Cells can also have multiple possible directions, here east and south, the agent can move towards.

</details>

### Schedule

Schedules define the start and end configurations of agents.

```
schedule(agentID,(start),(target),starting-orientation),earliest-departure.
    agentID              - unique identifier of the agent
    start                - (Y,X) initial position of agent
    target               - (Y,X) target of agent
    starting-orientation - orientation of the agent before departure
    earliest-departure   - timestep at which agent departs

```

<details>
<summary>Examples</summary>

```
schedule(1,(1,1),(4,2),e).
```

Represents the schedule of the agent with id 1. It starts at (1,1) with an eastward orientation and has to reach its target at (4,2).

</details>

## Difference

To move in a specific direction the difference between current position and new position has to be known.

```
diff(0, -1, 0). % North 
diff(1, 0, 1).  % East
diff(2, 1, 0).  % South
diff(3, 0, -1). % West
```

These are the four possible position differences. The application of them to a current position results in the new position.

## Limit

A limit should be applied in order to reduce excessive searches, the right limit depends on the environment. More precisely, it has to be sufficiently higher than the optimal solution of the environment requires.

```
limit(L).
```

<details>
<summary>Examples</summary>

```
limit(20).
```

Represents a limit of 20 time steps

</details>

[back to top](#railwayscheduling)

## Fact format: finding solutions
At each time step one possible direction is chosen. If the train halts, the direction at this time step is not specified.
```
direction(ID,D,T).
    ID  - agent ID
    D   - direction to go
    T   - time step
```

<details>
<summary>Examples</summary>

```
direction(0,1,0).
direction(0,2,2).
```
Agent `0` goes easterly `1` at time step `0`.
Agent `0` waits at time step `1`.
Agent `0` goes southerly at time step `2`.

</details>

---
The possible path is build from `trans`. The transition from cell A to cell B is defined for every time step.
```
trans(ID,(Y,X),(Y2,X2),O,T).
    ID      - agent ID
    (Y,X)   - from cell A
    (Y2,X2) - to cell B
    D       - orientation of train
    T       - time step
```

<details>
<summary>Examples</summary>

```
trans(3,(0,0),(0,1),1,5).
trans(3,(0,1),(1,1),2,6).
```
Agent `3` goes from cell `(0,0)` to cell `(0,1)` which is easterly `1` at time step `5`.
Agent `3` goes from cell `(0,1)` to cell `(1,1)` which is southerly `2` at time step `6`.

</details>

---
```
done(ID,T).
    ID      - agent ID
    T       - time step
```
Time step at which agent reached its goal and is `done`.

## Fact format: transforming into Flatland actions

```
agent_action(ID, 4,T)
```
`agent_action` represents the flatland action that the agent is taking at every time step. This is needed, so the solution can be fed into Flatland for evaluation.
#####Flatland Actions:
- no_op = 0
- left = 1
- forward = 2
- right = 3
- halt = 4

These actions are relative to the agent's orientation.

---
If the agent has no choice other than to take a right turn in a cell, it is a Forward action. So we introduce `count`. Right or Left actions are only used to choose between paths.
`count` represents the amount of choices `C` an agent has for every cell `(Y,X)` and orientation `O`.
```
count((Y,X),O,C).
    (Y,X)   - cell
    O       - orientation of agent
    C       - amount of choices
```
<details>
<summary>Examples</summary>

```
count((1,3),0,2).
```
Cell `(1,3)` has `2` choices when a train enters the cell with north `0` orientation

</details>

