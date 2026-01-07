import numpy as np
import os
import sys
import math

inf = 1000000000


def alg_naive():
	num_obj = int(sys.argv[1])
	num_loc = int(sys.argv[2])
	dis_max = int(sys.argv[3])
	
	fname = sys.argv[1]+"_"+sys.argv[2]+"_val_loc.txt"
	f = open(fname, "r")
	lines = f.readlines()
	linenum = len(lines)
	value = []
	loc = []
	for i in range(num_obj):
		value.append(int(lines[i]))
	for i in range(num_obj, linenum):
		a,b = lines[i].split()
		loc.append([int(a),int(b)])
	f.close()
	
	neigh = [[] for x in range(num_loc)]
	for i in range(num_loc):
		for j in range(num_loc):
			dis = math.sqrt((loc[i][0]-loc[j][0])*(loc[i][0]-loc[j][0]) + (loc[i][1]-loc[j][1])*(loc[i][1]-loc[j][1]))
			if dis < dis_max:
				neigh[i].append(j)
				neigh[j].append(i)
	
	fname = sys.argv[1]+"_"+sys.argv[2]+"_network.txt"
	f = open(fname, "r")
	lines = f.readlines()
	linenum = len(lines)
	net = [[] for x in range(num_obj)]
	num_edges = int(lines[0])
	for i in range(1, linenum):
		a,b,c,d = lines[i].split()
		a = int(a)
		b = int(b)-num_obj
		prob = float(d)/100.00
		if a<num_obj and b<num_obj+num_loc:
			# loc b, protect prob, protect value d*value[a]
			net[a].append([b,1-prob,(1-prob)*value[a]])
	f.close()
	
	obj2loc = [[-1,-1,-1] for x in range(num_obj)]
	loc2obj = [-1 for x in range(num_loc)]
	
	for d in range(num_obj):
		max_value = -inf
		o = -1
		l = -1
		p = -1
		pv = -1
		for i in range(num_obj):
			if obj2loc[i][0] > -1:
				continue
			for j in range(len(net[i])):
				lidx = net[i][j][0]
				prob = net[i][j][1]
				pval = net[i][j][2]
				if loc2obj[lidx] > -1:
					continue
				if pval > max_value:
					max_value = pval
					o = i
					l = lidx
					p = prob
					pv = pval
		if max_value > -inf:
			obj2loc[o][0] = l
			obj2loc[o][1] = p
			obj2loc[o][2] = pv
			loc2obj[l] = o
	
	
	protect_value = 0
	for i in range(num_loc):
		if loc2obj[i] > -1:
			obj = loc2obj[i]
			prob = obj2loc[obj][1]
			pval = obj2loc[obj][2]
			for x in neigh[i]:
				if loc2obj[x] > -1:
					pval = pval * obj2loc[loc2obj[x]][1]
			protect_value = protect_value + pval
	print("naive protected value: %f" % (protect_value))
	return protect_value					
	
	
	
	
	
if __name__ == "__main__":
	alg_naive()
