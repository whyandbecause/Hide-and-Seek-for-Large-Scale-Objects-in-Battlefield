import numpy as np
import math
import os
import matplotlib.pyplot as plt

def draw_plot2(lines, appendix):
	num = len(lines)
	i = -1
	flag = 0
	plt.figure(figsize=(10,8)) 
	while True:
		i = i + 1
		if i>=num:
			break
		t = lines[i].strip()	
		if t.find("alg_our.py 30 46") >= 0:
			dis_max = int(t.split()[4])
			print(dis_max)
			our = []
			opt = []	
			naive = []	
			for j in range(i, i+28):
				t = lines[j].strip()
				if t.find("our protected value") >= 0:	
					our.append(float(t.split()[-1]))
				if t.find("max probability value") >= 0:
					opt.append(float(t.split()[-1]))
				if t.find("naive protected value") >= 0:	
					naive.append(float(t.split()[-1]))
			i = i + 28				
			
			#x = [200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000]
			x = [150, 125, 100, 75, 50, 25, 10]
			plt.plot(x, our, color='red', linestyle='--', linewidth=5.0, label='our')
			plt.plot(x, opt, color='blue', linestyle='-', linewidth=5.0, label='mcmf')
			plt.plot(x, naive, color='green', linestyle='-.', linewidth=5.0, label='naive')
			plt.xlim(160, 1) 
			plt.legend(fontsize=25)
			#plt.title('D='+str(dis_max), size=30)
			plt.xlabel('Maximum distance', size=25)
			if flag == 0:
				plt.ylabel('Protected value', size=25)
			flag = 1
			plt.grid(True)
			#plt.xlim(0, 4)
			plt.ylim(0, 160)
			#plt.savefig('fig' +str(dis_max) + '.pdf')
			#plt.savefig('fig' +str(dis_max) + '_fix.pdf')

			plt.savefig('fig_plot_dis_real'+appendix+'.pdf')
			plt.show()
	
def draw_bar2(lines, appendix):
	num = len(lines)
	i = -1
	flag = 0	
	spidx = 0
	dlist = [50]
	
	while True:
		i = i + 1
		if i>=num:
			break
		t = lines[i].strip()	
		if t.find("alg_our.py 30 46") >= 0:
			dis_max = int(t.split()[4])
			print(dis_max)
			our = []
			opt = []	
			naive = []	
			for j in range(i, i+28):
				t = lines[j].strip()
				if t.find("our protected value") >= 0:	
					our.append(float(t.split()[-1]))
				if t.find("max probability value") >= 0:
					opt.append(float(t.split()[-1]))
				if t.find("naive protected value") >= 0:	
					naive.append(float(t.split()[-1]))
			i = i + 28			
			
			print(our, opt, naive)
			
			fig, ax = plt.subplots()
			categories = [150, 125, 100, 75, 50, 25, 10]
			x = np.arange(len(categories))
			print(x)
			width = 0.22
			ax.bar(x-width, naive, width, label='naive', color='Green')
			ax.bar(x, our, width, label='our', color='red')	
			ax.bar(x+width, opt, width, label='mcmf', color='royalBlue')	
			ax.set_xticks(x)	
			ax.set_xticklabels(categories)
			
			ax.legend(fontsize=30)
			#ax.set_title('D='+str(dis_max), size=30)
			ax.set_xlabel('Maximum distance', size=30)
			if flag == 0:
				ax.set_ylabel('Protected value', size=30)
			flag = 1
			plt.tight_layout()
			#plt.grid(True)
			#plt.xlim(0, 4)
			plt.ylim(0, 256)
			#plt.savefig('fig' +str(dis_max) + '.pdf')
			#plt.savefig('fig' +str(dis_max) + '_fix.pdf')
			plt.subplots_adjust(wspace =0.1, hspace =0)
			plt.savefig('fig_bar_dis_real'+appendix+'.pdf')
			plt.show()


def draw_plot(lines, appendix):
	num = len(lines)
	i = -1
	flag = 0
	plt.figure(figsize=(30,8)) 
	spidx = 0
	dlist = [500, 300, 100]
	while True:
		i = i + 1
		if i>=num:
			break
		t = lines[i].strip()	
		if t.find("alg_our.py 200 400") >= 0:
			dis_max = int(t.split()[4])
			if dis_max in dlist:
				print(dis_max)
				our = []
				opt = []	
				naive = []	
				for j in range(i, i+40):
					t = lines[j].strip()
					if t.find("our protected value") >= 0:	
						our.append(float(t.split()[-1]))
					if t.find("max probability value") >= 0:
						opt.append(float(t.split()[-1]))
					if t.find("naive protected value") >= 0:	
						naive.append(float(t.split()[-1]))
				i = i + 40				
				
				x = [_ for _ in range(200, 2001, 200)]
						
				spidx = spidx + 1
				plt.subplot(1,len(dlist),spidx)
				plt.plot(x, our, color='red', linestyle='--', linewidth=5.0, label='our')
				plt.plot(x, opt, color='blue', linestyle='-', linewidth=5.0, label='mcmf')
				plt.plot(x, naive, color='green', linestyle='-.', linewidth=5.0, label='naive')

				plt.legend(fontsize=30)
				#plt.title('D='+str(dis_max), size=30)
				plt.xlabel('# of objects, $d_{max}$='+str(dis_max) + " "+appendix, size=30)
				if flag == 0:
					plt.ylabel('Protected value', size=30)
				flag = 1
				plt.grid(True)
				#plt.xlim(0, 4)
				plt.ylim(-256, 10800)
				#plt.savefig('fig' +str(dis_max) + '.pdf')
				#plt.savefig('fig' +str(dis_max) + '_fix.pdf')

	plt.subplots_adjust(wspace =0.1, hspace =0)
	plt.savefig('fig_plot_dis_'+appendix+'531.pdf')
	plt.show()
	
def draw_bar(lines, appendix):
	num = len(lines)
	i = -1
	flag = 0	
	spidx = 0
	dlist = [400, 50]
	fig, axs = plt.subplots(nrows=1, ncols=len(dlist), figsize=(20, 8))
	while True:
		i = i + 1
		if i>=num:
			break
		t = lines[i].strip()	
		if t.find("alg_our.py 200 400") >= 0:
			dis_max = int(t.split()[4])
			if dis_max in dlist:
				print(dis_max)
				our = []
				opt = []	
				naive = []	
				for j in range(i, i+40):
					t = lines[j].strip()
					if t.find("our protected value") >= 0:	
						our.append(float(t.split()[-1]))
					if t.find("max probability value") >= 0:
						opt.append(float(t.split()[-1]))
					if t.find("naive protected value") >= 0:	
						naive.append(float(t.split()[-1]))
				i = i + 40				
				
				
				ax = axs[spidx]
				spidx = spidx + 1
				categories = [_ for _ in range(200, 2001, 200)]
				x = np.arange(len(categories))
				width = 0.25
				ax.bar(x-width, naive, width, label='naive', color='Green')
				ax.bar(x, our, width, label='our', color='red')	
				ax.bar(x+width, opt, width, label='mcmf', color='royalBlue')	
				ax.set_xticks(x)	
				ax.set_xticklabels(categories)
				
				ax.legend(fontsize=30)
				#ax.set_title('D='+str(dis_max), size=30)
				ax.set_xlabel('# of objects, $d_{max}$='+str(dis_max) + " "+appendix, size=30)
				if flag == 0:
					ax.set_ylabel('Protected value', size=30)
				flag = 1
				plt.tight_layout()
				#plt.grid(True)
				#plt.xlim(0, 4)
				#plt.ylim(-256, 10800)
				#plt.savefig('fig' +str(dis_max) + '.pdf')
				#plt.savefig('fig' +str(dis_max) + '_fix.pdf')
	plt.subplots_adjust(wspace =0.1, hspace =0)
	plt.savefig('fig_bar_dis_'+appendix+'45.pdf')
	plt.show()
		
if __name__ == "__main__":
	flist = ["res_dec.txt", "res_fix.txt"]
	for fname in flist:
		f = open(fname, "r")	
		appendix = fname.split("_")[1].split(".")[0]
		lines = f.readlines()
		f.close()
		draw_bar(lines, appendix)
		#draw_plot(lines, appendix)
		
