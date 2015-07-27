import numpy as np
from convnet_James import ConvolutionalNeuralNetwork
import random
from theano import tensor as T
# from load import mnist

class multi_net(object):

	def __init__(self):
		self.data_list=[]
		self.net_list = []
		self.task_id=1
		self.epochs=1
		self.batch_size=10
		self.data_set={}
		self.cnn = ConvolutionalNeuralNetwork()
		self.cnn.initialize_mnist()	
		self.trX_spf, self.trY_spf = self.split_data (self.cnn.trX, self.cnn.trY, 0)
		self.data_set[0] = [self.trX_spf, self.trY_spf]
		self.signal = True


	def create_cnn(self):
		self.cnn = ConvolutionalNeuralNetwork()
		self.cnn.initialize_mnist()	
		if self.task_id != 1:	
			self.cnn.load_all_weights(self.task_id-1)	
		self.cnn.create_model_functions()
		return self.cnn

	def shuffle_data(self, x, y):
		c=zip(x,y)
		random.shuffle(c)
		x, y=zip(*c)
		return x, y 	

	def get_sub_test_data(self):
		teX = self.cnn.teX
		teY = self.cnn.teY
		X = []
		Y = []
		for i in range(len(teX)):
			index = np.argmax(teY[i])
			if self.signal:
				if index <= self.task_id:
					X.append(teX[i,:,:,:])
					Y.append(teY[i])
			else:
				if index > self.task_id:
					X.append(teX[i,:,:,:])
					Y.append(teY[i])
		return X, Y


	def process_data(self):
		self.trX_spf, self.trY_spf = self.split_data (self.cnn.trX, self.cnn.trY, self.task_id)
		self.data_set[self.task_id] = [self.trX_spf, self.trY_spf]
		trX, trY, teX, teY = self. check_pre()
		trX, trY = self.shuffle_data(trX, trY)
		teX, teY = self.shuffle_data(teX, teY)
		return trX, trY, teX, teY

	def split_data(self, dataset, label, task_id):
		matching = np.nonzero(np.argmax(label, axis = 1) == task_id)[0]
		return dataset[matching], label[matching] 

	def run(self):
		for self.task_id in range(1,3):
			# if self.task_id == 0:
			# 	self.cnn = self.create_cnn()
			# 	trX, trY, teX, teY=self.process_data()
			# 	self.train(self.cnn, trX, trY, teX, teY)
			# 	self.cnn.save_all_weights(self.task_id)
			if len(self.net_list)-1 != self.task_id:
				self.cnn=self.create_cnn()
				trX, trY, teX, teY=self.process_data()
				self.train(self.cnn, trX, trY, teX, teY)
				self.cnn.save_all_weights(self.task_id)
			if len(self.net_list)-1 == self.task_id:
				pass
			self.net_list.append(self.cnn)
		# self.test()

	def check_pre(self):
		trX, trY, = self.data_set[self.task_id]
		# task_number=[self.task_id]
		if self.task_id >= 1:
			trX_1, trY_1 = self.data_set[self.task_id-1]
			trX = self.crossing_share_X(trX, trX_1, .8, trX)
			trY = self.crossing_share_Y(trY, trY_1, .8, trY)
			# task_number.append(self.task_id-1)

		if self.task_id >= 3:
			trX_2, trY_2 = self.data_set[self.task_id-3]
			trX = self.crossing_share_X(trX, trX_2, .6, trX)
			trY = self.crossing_share_Y(trY, trY_2, .6, trY)
			# task_number.append(self.task_id-2)

		if self.task_id >= 5:
			trX_3, trY_3 = self.data_set[self.task_id-5]
			trX = self.crossing_share_X(trX, trX_3, .4, trX)
			trY = self.crossing_share_Y(trY, trY_3, .4, trY)

		if self.task_id >= 7:
			trX_4, trY_4 = self.data_set[self.task_id-7]
			trX = self.crossing_share_X(trX, trX_4, .4, trX)
			trY = self.crossing_share_Y(trY, trY_4, .4, trY)

		if self.task_id >= 9:
			trX_4, trY_4 = self.data_set[self.task_id-9]
			trX = self.crossing_share_X(trX, trX_4, .2, trX)
			trY = self.crossing_share_Y(trY, trY_4, .2, trY)

		trX = np.asarray(trX)
		trY = np.asarray(trY)
		teX, teY = self.get_sub_test_data()
		teX = np.asarray(teX)
		teY = np.asarray(teY)
		print teX.shape
		print teY.shape
		print trX.shape
		print trY.shape
		return trX, trY, teX, teY

	def crossing_share_X(self, a, b, rate, c):
		index = rate*len(c)
		b = b[:index,:,:,:]
		a = np.concatenate((a, b), axis=0)
		return a

	def crossing_share_Y(self, a, b, rate, c):
		index = rate*len(c)
		b = b[:index,:]
		a = np.concatenate((a, b), axis=0)
		return a

	def train(self, cnn, trX, trY, teX, teY):
		signals=[]
		for i in range(self.epochs):
			for start, end in zip(range(0, len(trX), self.batch_size), range(self.batch_size, len(trX), self.batch_size)):
				cnn.cost = cnn.train(trX[start:end], trY[start:end])


			for start, end in zip(range(0, len(teX), self.batch_size), range(self.batch_size, len(teX), self.batch_size)):
				signal = cnn.predict(teX[start:end], teY[start:end])
				signals.extend(signal)
	
		if self.signal:

			print "{0}_in_range".format(self.task_id)
			np.save("{0}_in_range.npy".format(self.task_id),signals)
		else:
			print "{0}_out_range".format(self.task_id)
			np.save("{0}_out_range.npy".format(self.task_id),signals)


if __name__ == "__main__":
	mn=multi_net()
	mn.run()
	print "processing complete"