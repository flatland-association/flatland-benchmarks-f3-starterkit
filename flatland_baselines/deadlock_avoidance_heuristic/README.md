Shortest Path Deadlock Avoidance Heuristic
==========================================

👏Thanks to [aiAdrian](https://github.com/aiAdrian/flatland-benchmarks-f3-starterkit/tree/DeadLockAvoidancePolicy) for contributing!

### Problem description

Deadlock or over-filling is a situation in railway where two or more trains are blocking each other while asking
for resources. Let me explain it with the help of a simple example: train A holds resource X and asks for resource Y,
train B holds resource Y and asks for resource X;
due to the the circular resource allocation request,
Train A and train B will wait for each other forever.

![](https://gitlab.aicrowd.com/adrian_egli/flatland-challenge-starter-kit/-/raw/master/image/dead_lock_AB_XY.png)

Deadlock can occur in many situations where trains densly interacts on limited resource capacity, in particular if their path is predefined and fix.
To resolve deadlock at least one train has to travel backwards. But trains can only travel backwards in very limited situations.
Fixing deadlocks is a very complicated and in most cases very time consuming task.
In consequence, the railway simulation software must avoid deadlocks before they occur.

## Considerations about the problem complexity (classification)

#### Problem class: Shortest path only problem

Each instance of this problem class can be resolved by running the agents along their shortest path.
All agents have a disjunct shortest path.

#### Problem class: Shortest path and ordering problem

Each instance of this problem class can be solved by ordering agents in such a way
that they can travel along their shortest path but not ending in a deadlock situation.

#### Problem class: Require alternative path

Any instance of this problem class cannot be solved without at least one agent using a divergent route to their shortest path.

## Implemented method

To avoid deadlock situation we have invented a full-deterministic method. The runtime is quite cost intensive: O(n<sup>3</sup>), where
n is the maximum of [number of trains, max. number of resource in the train's travel path (cells)].

#### Algorithm

The proposed algorthim can find a feasible solution for any problem of the class: Shortest path and ordering problem.

##### Basic deadlock avoidance method

The algorithm collects for each train along its route all trains that are currently on a resource in the route.
For each collected train the method has to decide whether a deadlock between the train and the collected train occurs.
If no deadlock is found, the process must further decide at which position along the route the train must let pass the collected train.
This can be achieved by searching the train's path required resources backward along the path starting at the collected train position.
Stop the search when the resource along the collected train's path is not equal.
The forward and backward traveling along the train and the collected train path must be done step-by-step synchronous.
If the first non-equal resource position along the train's path is more than one resource from train's current location away,
then the train can move and no deadlock will occur for the next time step.

Since every agent can turn the travel direction at a dead end, the method must ensure that all variants of
"current" position is analyzed. Thus the deadlock avoidance method has to iterativly walk through all opposition agent
position, which is equal to the current position. That means, if the agents change traveling direction at a dead-end,
then the agent might visit again the "current" position. Or in other words the agent travels backward a part of the
forward path it has still passed through.  
Therefore the method has to test all sub-paths starting at "current position". This leads in an iteration over all
subpath. This can be quite cost intensive search.

![](https://gitlab.aicrowd.com/adrian_egli/flatland-challenge-starter-kit/-/raw/master/image/dead_lock_schema.png)

##### Deadlock avoidance extension for parallel action update

The method is still not sufficient to avoid deadlocks.
Because the flatland performs all actions in parallel.
This means that the update of each agent is not performed sequentially.
And flatland only checks whether the cell is free before agents move.
So it can happen that some agents take a step which would not be allowed. And deadlocks can occur. The agent doesn't have the
awareness of the potential conflict, because it did not watch the other agent. Both where hidden for the detection.

![](https://gitlab.aicrowd.com/adrian_egli/flatland-challenge-starter-kit/-/raw/master/image/dead_lock_paralell_actions.png)

Thus, the deadlock avoidance method must watch one step into the future. Only this ensures that the system is still deadlock free after a
action step (agent switch) is executed. So the method calculates possible deadlock one step in advance by propagating the agent's path and
all possible conflict pairs will be analized. To avoid deadlock, only one agent can enter into the critical section.  
The agent therefore propagate their paths one step ahead, and all another agent collect the agent whenever the next step
overlaps the agent's path. The the agent calculates for each agent pair whether it could avoid a deadlock or not by applying the
strategy describe. If there is no deadlock risk, only the agent with the highest priority can enter.

This is might to restritive. You might be able to workout a better strategy.

#### Examples

I'd like to explain in detail the following three examples:

Example A: The red train travels toward the green train.
Thus, the red train has to let pass the green train before the red train enters the shared part.
The latest position to let pass the green train is just before the red light located at the switch.
The green train does not see the red one along it's path. Thus, the green train doesn't collect any train.
The red train does see the green train along it's path, thus it has the green train collected. Now the red train starts
traveling backward it's path and tests where the green path differs. The green train can travel until this resource. There it has
to wait for the green train and it has to let pass the green train before the red train can continue its trip.

Example B: This example is very similar to the example A. The red train has to wait until the green train has passed.

Example C: The red train has to let cross the green train. It can wait at two different location. Just before the first
switch is the option 1. Or just before the 3rd switch is option 2. The question is what is the best location to cross.
This is not clear at the moment. This is an optimisation question, which can only be answered when an objective function
is known. But in this more restrictive variant, where we only have to avoid deadlock, we propose using the following strategy
which allows train passing as far as the can. Just stop a train a latest crossing point. Of course this changes dynamically during
simulation. Thus, in this example C the red train can pass the first two switches and has to wait for the crossing
green train just before the 3rd switch.

![](https://gitlab.aicrowd.com/adrian_egli/flatland-challenge-starter-kit/-/raw/master/image/dead_lock_ABC.png)

#### Limits

##### Known weakness

*Known weakness* in the current implementation, traffic jam can cause a deadlock situation.
The method does not propagate the required capacity a long the train's route. Thus, the train might no get the
required "space" to avoid a deadlock. Thus, if the railway system is very densely used and all the trains which have
to wait at a given location cannot fit into the crossing section (the capacity is not big enough for holding all trains in). Then they cause a jam and the
length of the jam might becomes to large, thus
trains no longer pass. And the whole methods fails. See the graphics below.

![](https://gitlab.aicrowd.com/adrian_egli/flatland-challenge-starter-kit/-/raw/master/image/dead_lock_jam.png)

*Known weakness* in the current implementation, travel direction change at dead-end can cause deadlock situations.
This is not yet detectable by the proposed method.

![](https://gitlab.aicrowd.com/adrian_egli/flatland-challenge-starter-kit/-/raw/master/image/weekness_dead_end.png )

##### Real world application

The proposed method does avoid deadlock by applying two principal operations: Stop moving and move along shortest path.
The method is therefore not powerful enough to solve all real world railway dispatching problems.
The method just ensures that no
deadlock or overfilling can occur if they can be avoided with these simple
operations STOP and MOVE. Thus, it can be that there is no solution without re-routing!
The propose method can detect deadlocks in advance thus a secondary re-routing
method could be called. But nevertheless the proposed method does not optimize the run time
nor any kind of objective function.

### Implemented dispatching strategy

All trains follow their shortest path. The implemented dispatching strategy does dispatch train by first-come-first-serve strategy. Thus, if two trains like
to get a resource (cell or rail) at a switch where two rails come together, then the first train will get the resource.
The first train is the train with the smaller index (env.agents[index]). This rule is applied, as long as the deadlock
avoidance method does not force to stop the train. A stopped train will not enter into a new section.
Thus the first-come-first-serve rule still works.

#### Heuristic rule implemented

To further optimize the reward function, a heuristic strategy might be helpful.
In the next step, if two trains move into a critical section, the system prioritizes the train
by descending distance to be traveled. The train with the longest distance to its target gets the priority.

## What will be needed to improve the behavior

The system must have a (re-)routing and train order strategy that can intelligently respond to uncertainties.
To optimize the objective function the system must be able to estimate the reward in a very early stage and must
be able to find an alternative solution whenever an infrastructure disruption occurs or
when other trains get unforeseen delayed or trains block resources unforeseen long because of infrastructure problems or
engine fault.



Links
-----

* https://github.com/aiAdrian/flatland_solver_policy/blob/main/policy/heuristic_policy/shortest_path_deadlock_avoidance_policy/deadlock_avoidance_policy.py
* https://github.com/matsim-org/matsim-libs/blob/e49d25e00dc0a29d3361ccfb941ed4f757afcf10/contribs/railsim/docs/deadlock-avoidance.md
* https://gitlab.aicrowd.com/adrian_egli/flatland-challenge-starter-kit/-/tree/master/solver/Google_OR_Tools?ref_type=heads
* https://gitlab.aicrowd.com/adrian_egli/flatland-challenge-starter-kit/-/blob/master/solver/Google_OR_Tools/FLATland_as_DeadLock_avoidance_problem.md?ref_type=heads
* https://gitlab.aicrowd.com/adrian_egli/flatland-challenge-starter-kit/-/tree/master/solver/Google_OR_Tools/images?ref_type=heads