import pprint
import sys
import random
import time

from tqdm import tqdm

class Bullet():	
	def __init__(self, speed, position, release_time):
		self.speed = speed
		self.position = position
		self.release_time = release_time

	def get_speed(self):
		return self.speed


	def get_position(self):
		return self.position


	def get_release_time(self):
		return self.release_time


	def set_position(self, new_position):
		if new_position > 0:
			self.position = new_position
		raise Exception

	def get_intercept(self):
		return self.release_time*self.speed

	def get_equation(self):
		return f'y={self.speed}x - {self.get_intercept()}'

	def __repr__(self):
		return f'Bullet {self.release_time}'# , {self.get_equation()}'
		# Speed: {self.speed}, Position: {self.position}, Release: {self.release_time}, Equation: {self.get_equation()}"

	def __str__(self):
		return f'Speed: {self.speed}, Position: {self.position}, Release: {self.release_time}, Equation: {self.get_equation()}"'


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
	return  bullets


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
	# random.setstate((3, (2147483648, 2134241387, 3766062456, 1238795968, 1894802142, 1907041398, 3098534405, 2308888036, 1837767852, 1501908445, 2283670039, 180892392, 2897975062, 551736828, 3902951719, 4260422867, 3036152728, 1400945861, 1508627746, 989805760, 3315180370, 1258273455, 1450590975, 1030243623, 935634625, 517253976, 281609586, 1575670994, 1684429101, 1267622367, 1735874000, 2351368398, 3310650636, 267093859, 2271663295, 599838289, 2018791084, 233800336, 2002717686, 1611759355, 374438805, 2701429500, 2112853581, 3492837444, 2113095379, 4045145472, 1432034859, 3918982657, 1913233976, 257290552, 3452385646, 2115251044, 2931787167, 3073137864, 3646862722, 1477670584, 3922464632, 4256252472, 1232900069, 1173573791, 2799757110, 1611500446, 549409631, 3613531653, 2509036570, 2313119260, 3942807069, 1480654764, 3351843871, 480259775, 1990168764, 1804409911, 4050620192, 324015484, 3431125853, 408524412, 759549116, 2389241084, 2239777018, 2109830556, 2642131881, 2083929679, 3048965432, 3074799773, 2363481716, 1489601665, 1268012513, 238114505, 183189324, 431706198, 2742558573, 2287058364, 2558352465, 3338787793, 1465694592, 2023260315, 3962481896, 2835745081, 1528563954, 981411533, 2861004140, 1037401093, 3853038063, 1203689376, 395308916, 1245213960, 331574143, 406334132, 74373250, 2070936556, 1071285265, 4102660415, 3183255427, 1789988108, 731339881, 2113611693, 4112338384, 2841771367, 1054158372, 2940918599, 2568927506, 3663370678, 835503119, 3133585233, 947073211, 3157798834, 1878392876, 2938359386, 2364455010, 2228228544, 3541700749, 3626132668, 799130264, 1392098361, 1808081619, 369823219, 2635806811, 2966125611, 3764669103, 3894616259, 3065600296, 1369630889, 1066374596, 1138586132, 214832234, 2566757801, 1121234935, 3990377470, 2804117563, 1516369896, 1592290868, 2797320729, 215917357, 3054935016, 54882683, 448161391, 2561245094, 4026266879, 3503668619, 3995033585, 2358650026, 2924612029, 2663489645, 1331801778, 547525922, 2825664359, 29942036, 1570885249, 323141018, 1108694916, 1591119583, 3758236692, 3198087815, 1944564902, 1069450165, 1306962016, 2883528953, 3776030157, 3712552237, 2906526463, 870374358, 56401033, 3133511289, 999370279, 2866785940, 4120153219, 2291343597, 2083361455, 1899691456, 4011725640, 1785012078, 1666169395, 2518010192, 811107865, 2798829171, 2911623630, 99554110, 2775591220, 4268880888, 3321272648, 2029142431, 225176827, 3585015052, 4159807054, 2412639834, 2806086686, 3399747883, 2462894053, 1455994018, 3280454420, 2588826755, 3334014745, 2970496925, 2276613431, 1286951207, 991575062, 3127938828, 2525958192, 2519455395, 497731527, 1515239784, 2349221171, 3148792576, 3626079165, 4064087317, 3800393366, 3656220933, 606188036, 500149705, 1264233370, 2720205217, 3802785238, 3977253159, 1600791222, 3797019206, 4207706422, 2208428029, 3785079187, 591721808, 3494152881, 4139978131, 508947723, 344655052, 3031031288, 2271476029, 2735491510, 1048264681, 4264030787, 1826140646, 950268708, 1065055359, 911493793, 588022500, 2649702194, 99954227, 740942354, 842239338, 1504785780, 1846456052, 2610990412, 355627645, 3981408264, 3451023607, 4026008872, 2600616656, 903480677, 412139202, 1970595, 3528836439, 3951238970, 779854700, 1219937526, 384310694, 1175752848, 3856079611, 2033795683, 3781405363, 2990262047, 1659121861, 1383097142, 2936965118, 852682666, 63531447, 636077867, 3508081462, 2487154735, 3993942587, 2865695105, 84184955, 3290542086, 4162627309, 720137955, 406590943, 50393062, 2524232350, 368594187, 3770863808, 2126894125, 762595859, 1574243234, 721594456, 3261273190, 1748077361, 3341124645, 2318578507, 2916516925, 2969083308, 3459784580, 1852743462, 2791970713, 3710147458, 433705718, 1811563977, 3857729206, 1315025194, 3982190362, 3969911786, 2744523951, 1950730077, 1257488270, 3952819112, 102723373, 1571513930, 4028536899, 2116379894, 2765280198, 3428140592, 4053376145, 764517497, 1761308040, 2324374011, 3959759183, 3105468813, 2440313414, 3197418697, 3231898606, 3981034075, 3700895609, 2181004599, 1940586422, 2726158091, 883743864, 3982394395, 3987417031, 4188754921, 1386419051, 3636017709, 2245231868, 168068502, 1192571464, 2492627107, 2472068549, 2483667750, 748258147, 3899327476, 4022795679, 2785437830, 1666875219, 2653728377, 2798640041, 2665076895, 300971225, 2149375566, 1746515333, 789683521, 1166530778, 3835565653, 1759640649, 1362644386, 2527995868, 210270362, 3216672575, 3022488698, 2072195021, 2426298681, 782070281, 4224250075, 3465405719, 428897327, 142421478, 3902230509, 3974632992, 131634026, 616024008, 3662151428, 2893437977, 2172356549, 1836881803, 1649161593, 1480297323, 3123170182, 2659783089, 1357105673, 3004154872, 2621917780, 509324162, 3181571620, 2609332895, 1301657210, 907582790, 337659020, 255915300, 1480505231, 2257284262, 1118905129, 1181477511, 4220102663, 4107990673, 2358493680, 1105584603, 2252017009, 3078362988, 940916521, 1679279929, 488778647, 2281668630, 3361767042, 2626931857, 3249105172, 4283005859, 630639338, 250190815, 3870711655, 3726911045, 4088849663, 2805621676, 2296724259, 3244979099, 2859748209, 886638091, 1654839759, 2698583792, 1978699745, 3721892244, 2996452549, 2938590676, 1985507731, 4209190732, 4256862372, 569674766, 1059458772, 1771405818, 3728870838, 2740448173, 3829161903, 4009840042, 1850836984, 514970619, 1692930474, 3935421316, 712896031, 3238470466, 251017741, 666655762, 2836378103, 1816226945, 654292637, 1680411881, 793987914, 1976400203, 3218272890, 3049677608, 2361717855, 1312635979, 1686771537, 1032410961, 3610517950, 319714051, 2263813519, 3044397639, 3207558334, 1273290466, 2509824777, 829291364, 480449131, 4133645204, 2347505569, 3219918767, 1041851519, 2997715778, 2569146477, 1153379293, 3262696488, 4017527543, 1353961241, 2783222134, 618687235, 940860596, 1687039611, 1577187963, 1284679027, 31768070, 2380795415, 1396850954, 2062116513, 775889650, 1388412662, 1543115557, 1877616141, 341854646, 1706876418, 2836358929, 3439995437, 1578179151, 4091779921, 3998093574, 702363674, 3035833897, 3552932902, 3762469699, 2712467319, 2314243550, 1551536513, 2265987227, 3873131225, 3562670032, 2917381525, 968241084, 360389200, 2535782649, 292472045, 2941187417, 3953140404, 1865207685, 3811941820, 445056153, 2548949096, 1239358273, 4244301563, 536873019, 3636161264, 2130974060, 4249767583, 3430922119, 1547693655, 838687580, 357848929, 3747291754, 2196591133, 3721380282, 641805405, 2461936793, 627781444, 1153762244, 3359553169, 3741305146, 194758584, 3730536424, 1119017425, 47678350, 2428294030, 3595477373, 3449959843, 1287187170, 3231711623, 1492527374, 8419508, 2393990631, 1270465658, 3810493725, 1950310976, 2012396776, 2155966546, 1089787810, 4120953383, 1988383252, 2172599613, 2943990472, 2025594471, 1370028589, 3558692075, 1650266680, 2199778242, 857614977, 968057915, 2435246832, 854841850, 3186007843, 1477552943, 57420722, 4095852911, 2657489493, 634263256, 1040705980, 3454486629, 1488505034, 155281323, 3806010818, 3235463216, 1908043530, 1099711218, 641209225, 2887030730, 1786741488, 209251285, 569684553, 644818915, 3041917995, 170440616, 3081507326, 2991503982, 3967745469, 1875948861, 2383231987, 1118344510, 3957057055, 1126073330, 2555425462, 1031928670, 1903755539, 1784635730, 3898641276, 3088154129, 694790241, 2758308177, 2629024427, 2233682267, 513739629, 97724535, 552666351, 2754545225, 374526362, 979388891, 3014773007, 624), None))
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
	with open('all_tests.csv', 'a+') as f:
	    sys.stdout = f # Change the standard output to the file we created.
	    print(f'{N=}, {trials=}, {k=}, {success=}, {failures=}, p={success/trials}, {draw=}')
	    sys.stdout = original_stdout # Reset the standard output to its original value


start_time = time.time()
n_range = [i for i in range(14, 15, 2)]
trial_range = [10**i for i in range(4, 5)]
k_range = [10*i for i in range(20, 21)]
for n in tqdm(n_range):
	for trials in tqdm(trial_range):
		for k in tqdm(k_range):
			main(N=n, trials=trials, k=k, debug=False)
print("%s seconds" % (time.time() - start_time))
print(f'{len(n_range)*len(trial_range)*len(k_range)} experiments' )
# test_check_for_duplicates()
