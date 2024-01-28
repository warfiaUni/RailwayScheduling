# Test And Benchmarking Environments

## Test Environments

These environments are built to test for basic behaviour like direction decisions, halting and collision detection.

### Simple Switch

A single agent has to decide which path to take on a simple switch. This environment provides a first test of an agent making a choice to reach its destination.

<p align="center">
<img width="400" src="https://raw.githubusercontent.com/warfiaUni/RailwayScheduling/media/media/2x3x1-simple_switch.png">
</p>

<details>
<summary>Tests</summary>

- dead ends
- switches
- decision making

</details>

### Crossing

A two agent map which requires one agent to wait and let the other agent pass.

<p align="center">
<img width="400" src="https://raw.githubusercontent.com/warfiaUni/RailwayScheduling/media/media/5x5-crossing.png">
</p>

<details>
<summary>Tests</summary>

- straights
- crossing
- halting
- collision detection

</details>

### Simple Dead End Passing

A slight variation of the [Simple Switch](#simple-switch) with multiple agents. One agent has to take a different path in order to prevent collisions. Specifically the turning behaviour of dead ends is tested on this map.

<p align="center">
<img width="400" src="https://raw.githubusercontent.com/warfiaUni/RailwayScheduling/media/media/2x3x2-switch_dead_end_passing.png">
</p>

<details>
<summary>Tests</summary>

- dead ends
- switches
- halting
- collision detection

</details>

## Edge Cases And Benchmarking Environments

These environments are purposefully designed to challenge encodings in satisfiability (by creating instances that are technically allowed in Flatland but still unsatisfiable) as well as solving time.

> **Disclaimer:**
> Some of these environments may require a custom line generator

## Simple Order

Two agents have to arrive in a specific order. The agent starting in `(0,0)` has to wait for the other agent to pass first.

<p align="center">
<img width="400" src="https://raw.githubusercontent.com/warfiaUni/RailwayScheduling/media/media/3x5x2-simple_order.png">
</p>

<details>
<summary>Tests</summary>

- straights
- curves
- switches
- halting
- timing
- collision detection

</details>

### Wait Or Late

In this environment one agent has the decision to either halt or take a very long route to their destination.

<p align="center">
<img width="400" src="https://raw.githubusercontent.com/warfiaUni/RailwayScheduling/media/media/7x15x2-wait_or_late.png">
</p>

<details>
<summary>Tests</summary>

- dead ends
- straights
- curves
- switches (normal and mirrored)
- halting
- collision detection
- timing

</details>

### No Exit

This environment specifically tests for basic satisfiability, more precisely reachability of the goal. Agents can enter the cyclic track, but there is no way to leave it.

<p align="center">
<img width="400" src="https://raw.githubusercontent.com/warfiaUni/RailwayScheduling/media/media/4x3x1-no_exit.png">
</p>

<details>
<summary>Tests</summary>

- straights
- curves
- switches (normal and mirrored)
- reachability

</details>

## Single Cycle

Up to four agents have to reach their destinations with the track containing a single loop.

<p align="center">
<img width="400" src="https://raw.githubusercontent.com/warfiaUni/RailwayScheduling/media/media/3x4-single_cycle.png">
</p>

<details>
<summary>Tests</summary>

- dead ends
- switches (normal and mirrored)
- collision detection
- cyclic behaviour

</details>

## Four Cycle

A larger variant of the [Single Cycle](#single-cycle) environment.

> **Warning:**
> Not accounting for cyclic behaviour in the encoding may result very long solving times

<p align="center">
<img width="400" src="https://raw.githubusercontent.com/warfiaUni/RailwayScheduling/media/media/3x10-four_cycle.png">
</p>

<details>
<summary>Tests</summary>

- dead ends
- switches (normal and mirrored)
- collision detection
- cyclic behaviour

</details>
