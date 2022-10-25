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
import pprint
import sys
import random
import time

from tqdm import tqdm

from bullet import Bullet


def get_state(message, bullets):
	pp = pprint.PrettyPrinter(indent=4)
	print()
	pp.pprint(message)
	pp.pprint([bullet.get_release_time() for bullet in bullets])
	pp.pprint([bullet.get_position() for bullet in bullets])
	pp.pprint([bullet.get_speed() for bullet in bullets])


def propose_advance(bullets):
	new_bullets = []
	for bullet in bullets:
		speed = bullet.get_speed()
		position = bullet.get_position()
		new_position = position + speed
		new_bullets.append(Bullet(speed, new_position, bullet.get_release_time()))
	return new_bullets


def check_bullet_in_bullets(bullet, bullets, debug=False):
	if debug:
		get_state('Checking if bullet in list of bullets', bullets)
	found = False
	b_id = bullet.get_release_time()
	speed = bullet.get_speed()
	for bullet_compare in bullets:
		if debug:
			print()
			print(bullet_compare.get_release_time(), bullet_compare.get_speed(), bullet_compare.get_position())
		if b_id == bullet_compare.get_release_time() and speed == bullet_compare.get_speed():
			found = True
	return found

def update_state(bullets, bullets_updated, time, collisions, debug=False):
	"""Returns updated list of bullets after those that have collided are removed

	FAILS in case of multiple collisions
	"""	

	if debug:
		print()
		print('UNSORTED', collisions)
	def get_point(collision):
		return collision[2]
	collisions = sorted(collisions, key=get_point)
	if debug:
		print('SORTED', collisions)

	all_bullets_to_remove = set()
	for collision in collisions:
		if collision[0] in all_bullets_to_remove or collision[1] in all_bullets_to_remove:
			continue
		all_bullets_to_remove.add(collision[0])
		all_bullets_to_remove.add(collision[1])
	if debug:
		print('all bullets to remove: ', all_bullets_to_remove)

	while len(all_bullets_to_remove) > 1:
		if debug:
			print(f'all bullets to remove {all_bullets_to_remove}')
		# remove first collision bullets from bullet list
		collision = collisions.pop(0)
		if debug:
			print(f'removing bullets in collision {collision}')

		bullet_0 = collision[0]  # first bullet involved in earliest collision
		bullet_1 = collision[1]  # second bullet involved in earliest collision
		found0 = check_bullet_in_bullets(bullet_0, bullets_updated, debug=debug)
		found1 = check_bullet_in_bullets(bullet_1, bullets_updated, debug=debug)
		if not (found0 and found1):
			continue
		point = collision[2]

		if debug:
			print()
			get_state('UPDATED: ', bullets_updated)
		new_bullets = []
		for bullet in bullets_updated:
			if debug:
				print()
				print(f'{bullet=}')
				print(f'{bullets_updated=}')
			bullet_id = bullet.get_release_time()
			if debug:
				print(f'{bullet_id=}')
				print(f'{bullet_0.get_release_time()=}')
				print(f'{bullet_1.get_release_time()=}')
			if bullet_id == bullet_0.get_release_time() or bullet_id == bullet_1.get_release_time():
				all_bullets_to_remove.discard(bullet_0)
				all_bullets_to_remove.discard(bullet_1)
				if debug:
					print(f'{all_bullets_to_remove=}')
				continue
			new_bullets.append(bullet)
		bullets_updated = new_bullets
		if debug:
			get_state('NEW: ', new_bullets)
			get_state('UPDATED_PRIME: ', bullets_updated)
			print(f'all bullets to remove {all_bullets_to_remove}')
	return new_bullets


def check_for_collisions(bullets, bullets_updated, time, debug=False):
	if debug:
		print(f'Time: {time}')
	collisions = []
	for index, bullet in enumerate(bullets):
		others = [x for i, x in enumerate(bullets) if i > index]
		for other in others:
			
			if debug: 
				get_state('Bullets former state', bullets)
				get_state('Bullets new state', bullets_updated)
				print(bullet)
				print(bullet.get_speed())
				print(bullet.get_release_time())
				print(other)
				print(other.get_speed())
				print(other.get_release_time())
			collision_point = (bullet.get_intercept() - other.get_intercept()) / (bullet.get_speed() - other.get_speed())
			if collision_point < 0 or bullet.get_release_time() > time or other.get_release_time() > time:
				continue
			if debug:
				print('Bullets Involved', bullet.get_release_time(), other.get_release_time())
				print(bullet.get_speed(), other.get_speed())
				print(time-1, collision_point, time)
				print()
			if time - 1 < collision_point and collision_point < time:
				if debug:
					print(collision_point)
				collisions.append((bullet, other, collision_point))
	if debug:
		print(f'Collisions: {collisions}')
	if collisions:
		if debug:
			print(f'Has collisions: {collisions}')
		output = update_state(bullets, bullets_updated, time, collisions, debug=debug)
		return output
	return bullets_updated


def check_for_leader(bullets):
	leader_speed = bullets[0].get_speed()
	all_speeds = [bullet.get_speed() for bullet in bullets]
	if leader_speed == max(all_speeds):
		return True
	return False	


def check_for_empty(bullets):
	return len(bullets) == 0


def step(bullets, time, debug=False):
	"""Advance the state by 1 time second"""
	has_runaway = check_for_leader(bullets)
	# print(f'Has runaway leader: {has_runaway}')
	bullets_updated = propose_advance(bullets)
	# get_state('PROPOSAL', bullets_updated)
	bullets_updated = check_for_collisions(bullets, bullets_updated, time, debug=debug)
	has_failed = check_for_empty(bullets_updated)
	return bullets_updated, has_runaway, has_failed

	
def refresh_bullets(N, debug=False):
	bullets = []
	for i in range(N):
		# bullet_speeds.append(random.uniform(SPEED_LOWER_BOUND, SPEED_UPPER_BOUND)) # [0, 1]
		speed = random.random() # [0, 1)
		bullets.append(Bullet(speed, -i*speed, i))
	# Test case
	# speed = [0.11, 0.25, 0.99, 0.01]
	# speed = [0.11, 0.15, 0.99, 0.01]
	"""speed = [0.10685989677476015, 0.12197633229148497, 0.012763812573190148, 0.5542827822857166]
	bullets.append(Bullet(speed[0], -0*speed[0], 0))
	bullets.append(Bullet(speed[1], -1*speed[1], 1))
	bullets.append(Bullet(speed[2], -2*speed[2], 2))
	bullets.append(Bullet(speed[3], -3*speed[3], 3))"""
	if debug:
		get_state('START', bullets)
	return bullets


def check_for_duplicates(bullets, tolerance=1e-2, debug=False):
	"""Returns True if any bullet speeds are within tolerance of each other"""
	if debug:
		print()
		print('CHECKING')
	for index, bullet in enumerate(bullets):
		if debug:
			print()
			print(f'bullet: {bullet}')
		others = [bullet for i, bullet in enumerate(bullets) if i > index]
		if len(others) == 0:
			continue
		if debug:
			print(others)
		speeds = [bullet.get_speed() for bullet in others]
		if debug:
			print(speeds)
		diffs = [abs(bullet.get_speed() - speed) for speed in speeds]
		if debug:
			print(diffs)
		if min(diffs) < tolerance:
			return True
	return False

def test_check_for_duplicates():
	test_harness = [
		(
			[
				Bullet(0.1, 0, 1),
				Bullet(0.2, 0, 1),
			], False
		),
		(
			[
				Bullet(0.1, 0, 1),
				Bullet(0.1, 0, 1),
			], True 
		),
		(
			[
				Bullet(0.1, 0, 1),
				Bullet(0.2, 0, 1),
				Bullet(0.3, 0, 1),
				Bullet(0.4, 0, 1),
			], False 
		),
	]
	print('Begin testing check_for_duplicates')
	for test_case in test_harness:
		assert check_for_duplicates(test_case[0]) == test_case[1]
	print('End testing check_for_duplicates')

def main(N, trials, k, debug=False):
	# N = 6
	# trials = 10000
	# k = 20
	# debug = False
	SPEED_LOWER_BOUND = 0
	SPEED_UPPER_BOUND = 1
	seed = random.getstate()
	print(f'{seed}')

	success = 0
	failures = 0
	draw = 0
	for trial in range(trials):
		# if trial == 875:
			# debug = True
		# else:
			# debug = False
		if debug:
			print(f'TRIAL {trial}')
		found_acceptable_bullets = False
		while not found_acceptable_bullets:
			bullets = refresh_bullets(N, debug=debug)
			if debug:
				get_state(f'BEFORE CHECKING', bullets)
			unacceptable_bullets = check_for_duplicates(bullets, debug=debug)	
			if not unacceptable_bullets:
				found_acceptable_bullets = True
		for time in range(1, k):
			bullets, has_succeeded, has_failed = step(bullets, time, debug=debug)
			if has_succeeded:
				if debug:
					print(f'Trial:{trial}, time:{time},  SUCCESS')
				success += 1
				break
			if has_failed:
				if debug:
					print(f'Trial:{trial}, time:{time},  FAILURE')
				failures += 1
				break
			if debug:
				get_state(f'After Step {time}', bullets)
		# TODO: Add in extension, code up to a limited time
		if not (has_succeeded  or has_failed):
			if debug:
				print(f'Trial:{trial}, time:{time},  DRAW')
			draw += 1

		if trial % 1000 == 0 and trial > 0:
			print(f'Trials:{trial}, Success:{success}, Failures:{failures}, Draws:{draw} P:{success/trial}')
			

	print(f'Trials:{trials}, Success:{success}, Failures:{failures}, Draws:{draw}, P:{success/trials}')
	original_stdout = sys.stdout
	with open('all_tests_simulation_method.csv', 'a+') as f:
	    sys.stdout = f # Change the standard output to the file we created.
	    print(f'{N=}, {trials=}, {k=}, {success=}, {failures=}, p={success/trials}, {draw=}')
	    sys.stdout = original_stdout # Reset the standard output to its original value


if __name__ == '__main__':
	start_time = time.time()
	n_range = [i for i in range(4, 11, 2)]
	trial_range = [10**i for i in range(1, 6)]
	k_range = [10*i for i in range(20, 21)]
	for n in tqdm(n_range):
		for trials in tqdm(trial_range):
			for k in tqdm(k_range):
				main(N=n, trials=trials, k=k, debug=False)
	print("%s seconds" % (time.time() - start_time))
	print(f'{len(n_range)*len(trial_range)*len(k_range)} experiments' )
	# test_check_for_duplicates()
