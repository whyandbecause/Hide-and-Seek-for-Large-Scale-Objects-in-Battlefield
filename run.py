import numpy as np
import math
import os

def gendata(m, n, fname):
	f = open(fname, "w")	
	
	data = []
	num = 0
	inf = 1000000000
	
	#gen edge(u, v, f, c)
	for i in range(m):
		for j in range(n):
			if np.random.randint(0, 10)<2:
				w = np.random.randint(1,100)
				num = num + 1
				data.append([i,m+j, 1, w])
				
	#gen edge(s, u, 1, 0), s=n+m
	for i in range(m):
		num = num + 1
		data.append([n+m, i, 1, 0])
		
	#gen edge(v, t, 1, 0), t=n+m+1
	for j in range(n):
		num = num + 1
		data.append([m+j, n+m+1, 1, 0])
	f.write("%d\n" % num)
	for x in data:
		f.write("%d %d %d %d\n" % (x[0], x[1], x[2], x[3]))
	f.close()
	
def gendata2(m, n):	
	f = open("30_46_p.txt", "r")
	pr = f.readlines()
	f.close()
	f = open("30_46_network.txt", "w")
	f.write("%d\n" % (30*46+30+46))
	for i in range(m):
		for j in range(n):
			f.write("%d %d %d %d\n" % (i, m+j, 1, int(float(pr[j].strip())*100)))
	for i in range(m):
		f.write("%d %d %d %d\n" % (n+m, i, 1, 0))
	for j in range(n):
		f.write("%d %d %d %d\n" % (m+j, n+m+1, 1, 0))
	f.close()
			
def gen_value_location(m, n, fname):
	f = open(fname, "w")	
	for j in range(m):
		f.write("%d\n" % (np.random.randint(1, 10)))
	for j in range(n):
		x = np.random.randint(0, 1000)
		y = np.random.randint(0, 1000)
		f.write("%d %d\n" % (x,y))
	f.close()


gendata2(30,46)
dis_list = [500, 400, 300, 200, 100, 50]
num_ve = [[30,46], [200,400],[400,800],[600,1200],[800,1600],[1000,2000],[1200,2400],[1400,2800],[1600,3200],[1800,3600],[2000,4000]]
num_ve = [[30,46]]
dis_list = [150, 125, 100, 75, 50, 25, 10]
for dd in dis_list:                                              
	for ve in num_ve:
		m = ve[0]
		n = ve[1]

		fname1 = str(m)+"_"+str(n)+"_network.txt"
		#gendata(m, n, fname1)
		fname2 = str(m)+"_"+str(n)+"_val_loc.txt"
		#gen_value_location(m, n, fname2)
		os.system("g++ mincostmaxflow.cpp -o mincostmaxflow")
		cmd = "./mincostmaxflow "+ str(m) + " " + str(n) + " " + fname1
		print(cmd)
		os.system(cmd)
		
		#dis_max = int(dd/math.sqrt(m/200))
		dis_max = int(dd)
		fname3 = str(m)+"_"+str(n)+"_result.txt"
		cmd = "python3 alg_our.py " + str(m) + " " + str(n) + " " + str(dis_max) + " " + fname3
		cmd2 = "python3 alg_naive.py " + str(m) + " " + str(n) + " " + str(dis_max)
		#print(cmd)
		os.system(cmd)
		os.system(cmd2)
		
