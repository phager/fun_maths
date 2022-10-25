"""Prompt: Imagine a gun which fires N = 2m | 0 < m \in Z bullets every second with a uniformly
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
"""
import itertools
import random
import sys
import time
	
from tqdm import tqdm

from bullet import Bullet
from bullets import get_state, refresh_bullets


def initialize_bullets(n, debug=False):
	"""Returns set of bullets"""
	return refresh_bullets(n, debug)


def construct_intersections(bullets, debug=False):
	"""Creates combos of bullets and prunes negative intersecting bullets"""
	# TODO: refactor into multiple methods
	if debug:
		cross = itertools.combinations(bullets, 2)
		print('Cross',[i for i in cross])
	output = []
	cross = itertools.combinations(bullets, 2)
	for bullet_pair in cross:
		# collision_time is the x-value (time) when the two lines intersect
		collision_time = (bullet_pair[0].get_intercept() - bullet_pair[1].get_intercept()) \
			/ (bullet_pair[0].get_speed() - bullet_pair[1].get_speed())

		# collision height
		if debug:
			print()
			print(f'{bullet_pair=}')
			print(f'{collision_time=}')

		# collision_location is the y-value (distance) when the two lines intersect
		# y = mx - b
		collision_location_0 = bullet_pair[0].get_speed()*collision_time - bullet_pair[0].get_intercept()
		collision_location_1 = bullet_pair[1].get_speed()*collision_time - bullet_pair[1].get_intercept()
		# TODO add threshold argument to method
		assert (collision_location_0 - collision_location_1) < 1e-1

		# collision locations
		if debug:
			print(f'{collision_location_0=}')
			print(f'{collision_location_1=}')

		# Prune intersections that occur when x<0 and when y<0 

		# if collision point is negative do not add to list
		if collision_time < 0 or collision_location_1 < 0 or collision_location_1 < 0:
			continue
		collision = (bullet_pair[0], bullet_pair[1], collision_time)
		output.append(collision)
	if debug:
		print('post initialization')
		print(f'{output=}')
	return output


def intersection_sorting_fn(intersection):
	return intersection[2]


def extract_bullets(intersection, debug=False):
	return intersection[0], intersection[1]


def remove_bullet(bullets, bullet_to_remove, debug=False):
	output = []
	for bullet in bullets:
		if bullet == bullet_to_remove:
			continue
		output.append(bullet)
	if debug:
		print(output)

	return output



def remove_future_intersections(intersections, bullet, debug=False):
	"""Delete from consideration all intersections that contain the bullet.

	:param:intersections
	:param:bullet
	:param:debug
	"""
	output = []
	for intersection in intersections:
		bullet_0, bullet_1 = extract_bullets(intersection, debug)
		if bullet == bullet_0 or bullet == bullet_1:
			continue
		output.append(intersection)
	return output


def run_trial(n, debug=False):
	bullets = initialize_bullets(n, debug)

	if debug:
		get_state(f'BEFORE CHECKING', bullets)

	intersections = construct_intersections(bullets, debug) # prunes negative intersections

	if debug:
		print(f'Pre sort {intersections=}')

	intersections = sorted(intersections, key=intersection_sorting_fn)

	if debug:
		print(f'Post sort {intersections=}')

	# TODO: Add optimization which checks for membership within intersections otherwise skip and return success
	
	while intersections:
		intersection = intersections.pop(0)

		if debug:
			print(f'{intersection=}')

		bullet_0, bullet_1 = extract_bullets(intersection)

		bullets = remove_bullet(bullets, bullet_0, debug)
		intersections = remove_future_intersections(intersections, bullet_0, debug)
		bullets = remove_bullet(bullets, bullet_1, debug)
		intersections = remove_future_intersections(intersections, bullet_1, debug)

		if debug:
			print()
			print(f'Post intersection {intersections=}')


	return len(bullets) > 0
	



def main(N, trials, debug=False):
	"""
	:param: N the number of bullets | N % 2 == 0
	:param: trials the number of repeated trials
	:param: k the number of simulation steps
	:param: debug whether to print verbose state and error messages
	"""
	debug = debug
	SPEED_LOWER_BOUND = 0
	SPEED_UPPER_BOUND = 1
	seed = random.getstate()
	if debug:
		print(f'{seed}')

	success = 0
	failures = 0
	draw = 0
	if debug:
		print(f'Trials:{trials}, Success:{success}, Failures:{failures}, Draws:{draw}, P:{success/trials}')

	for trial in range(trials):
		if debug:
			print(f'TRIAL {trial}')

		# if trial == 875:
			# debug = True
		# else:
			# debug = False
		result = run_trial(N, debug)
		if result:
			if debug:
				print(f'Trial:{trial}, SUCCESS')
			success += 1
		else:
			if debug:
				print(f'Trial:{trial}, FAILURE')
			failures += 1
		if trial % 1000 == 0 and trial > 0:
			print(f'Trials:{trial}, Success:{success}, Failures:{failures}, Draws:{draw} P:{success/trial}')
	print(f'Trials:{trials}, Success:{success}, Failures:{failures}, Draws:{draw}, P:{success/trials}')

	original_stdout = sys.stdout
	with open('all_tests_intersection_method.csv', 'a+') as f:
	    sys.stdout = f # Change the standard output to the file we created.
	    print(f'{N=}, {trials=}, k=0, {success=}, {failures=}, p={success/trials}, {draw=}')
	    sys.stdout = original_stdout # Reset the standard output to its original value
			

if __name__ == '__main__':
	start_time = time.time()
	n_range = [i for i in range(4, 5, 2)]
	trial_range = [10 for i in range(4, 5)]
	for n in tqdm(n_range):
		for trials in tqdm(trial_range):
			main(N=n, trials=trials, debug=True)

	print("%s seconds" % (time.time() - start_time))
	print(f'{len(n_range)*len(trial_range)} experiment[s]' )
