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
