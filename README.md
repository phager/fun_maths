# Problem
Imagine a gun which fires N = 2m | 0 < m \in Z bullets every second with a uniformly
random speed [0, 1] m/s in a single direction in a vacuum. When two bullets collide they both
disappear. What is the probability of a[ny] bullet escape[ing] as time approaches infinity?

Escaping is defined as not disappearing continuing on without collision forever.

e.g.
m = 1
N = 2
s_0 = 0.1
s_1 = 0.9

Bullet 0 is fired at t=0, traveling at 0.1m/s
Bullet 1 is fired at t=1, traveling at 0.9m/s
Bullet 0 and Bullet 1 collide at time t=1.125 and both disappear
Neither bullet escapes

![plot](./output.jpg)

# Experimental Approximations
| N	| p	|
| ----- | ----- |
| 2 	| 0.5	|
| 4 	| 0.625	|
| 6 	| 0.69	|
| 8 	| 0.72	|
| 10 	| 0.75	|


# Simulation Method
`python bullets.py > output.txt`

# Linear Calculation Method
`python lines.py > output.txt`
