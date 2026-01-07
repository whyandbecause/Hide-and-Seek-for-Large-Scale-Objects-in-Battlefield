import numpy as np
import os
import sys
import math

inf = 1000000000

def protect(obj2loc, loc2obj, neigh, label, num_obj, num_loc):
	protect_value = 0
	for i in range(num_loc):
		if label[i] == 1:
			obj = loc2obj[i]
			prob = obj2loc[obj][3]
			value = obj2loc[obj][4]
			p = (1-prob)*value
			for v in neigh[i]:
				if label[v] == 1:
					p = p * (1-obj2loc[loc2obj[v]][3])
			protect_value = protect_value + p	
	return protect_value
	
def weight_independent_set(obj2loc, delta, neigh, num_obj, num_loc):
	label = [-2 for x in range(num_loc)]
	for i in range(num_obj):
		label[obj2loc[i][1]] = -1
	for j in range(num_obj):
		minweight = inf
		obj = -1
		for i in range(num_obj):
			if label[obj2loc[i][1]] == -1:
				#print(i, obj2loc[i][1], delta[obj2loc[i][1]], obj2loc[i][3], obj2loc[i][4])
				w = delta[obj2loc[i][1]]/((1-obj2loc[i][3]) * obj2loc[i][4])
				if w < minweight:
					minweight = w
					obj = i
		if obj == -1:
			break
		#print(obj, obj2loc[obj][1], delta[obj2loc[obj][1]], (1-obj2loc[obj][3])*obj2loc[obj][4])
		label[obj2loc[obj][1]] = 1
		for v in neigh[obj2loc[obj][1]]:
			label[v] = 0
			delta[v] = delta[v] - 1
	return label

def get_loc_neigh_delta(obj2loc, num_obj, num_loc, dis_max):
	neigh = [[] for x in range(num_loc)]
	delta = [0 for x in range(num_loc)]		
	for i in range(num_obj):
		for j in range(i+1, num_obj):
			dis = math.sqrt((obj2loc[i][5]-obj2loc[j][5])*(obj2loc[i][5]-obj2loc[j][5]) + (obj2loc[i][6]-obj2loc[j][6])*(obj2loc[i][6]-obj2loc[j][6]))
			factor = (dis/dis_max)*(dis/dis_max)
			if factor < 1:
				x = obj2loc[i][1]
				y = obj2loc[j][1]
				neigh[x].append(y)
				neigh[y].append(x)
				delta[x] = delta[x] + 1
				delta[y] = delta[y] + 1
	return neigh, delta
	
def alg_our():
	f = open(sys.argv[-1], "r")
	num_obj = int(sys.argv[1])
	num_loc = int(sys.argv[2])
	dis_max = int(sys.argv[3])
	lines = f.readlines()
	obj2loc = []
	loc2obj = [-1 for x in range(num_loc)]
	for line in lines:
		x = line.split()
		#                 obj         loc             flow     probability         value     loc.x     loc.y
		obj2loc.append([int(x[0]),int(x[1])-num_obj, int(x[2]), int(x[3])/100.0, int(x[4]),int(x[5]),int(x[6])])
		loc2obj[int(x[1])-num_obj] = int(x[0])
	f.close()
	#print(a)
	#print(loc2obj)
		
	
	neigh, delta = get_loc_neigh_delta(obj2loc, num_obj, num_loc, dis_max)	
	#for i in range(len(neigh)):
	#	print(i, neigh[i], delta[i])
	
	#label: 1 for select, 0 for donot select, -1 for has object		
	label = weight_independent_set(obj2loc, delta, neigh, num_obj, num_loc)
	
	protect_value = protect(obj2loc, loc2obj, neigh, label, num_obj, num_loc)
		
	for _ in range(num_loc):
		gain_max = -100000
		gain_loc = -1
		for i in range(num_loc):
			if label[i] == -1 or label[i] == 0:
				temp = label[i]
				label[i] = 1
				gain = protect(obj2loc, loc2obj, neigh, label, num_obj, num_loc)
				if gain > protect_value and gain_max < gain:	
					gain_max = gain
					protect_value = gain
					gain_loc = i
				label[i] = temp
		if gain_loc == -1:
			break
		label[gain_loc] = 1
	
	protect_value = protect(obj2loc, loc2obj, neigh, label, num_obj, num_loc)
	cmd = "python3"
	for x in sys.argv:
		cmd = cmd + " " + x
	print(cmd)
	print("our protected value: %f" % (protect_value))
	
	opt = 0
	for i in range(num_obj):
		opt = opt + (1-obj2loc[i][3])*obj2loc[i][4]
	print("max probability value: %f" % (opt))
	return opt
	
	
if __name__ == "__main__":
	alg_our()
