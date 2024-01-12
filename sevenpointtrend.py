#	Written by  R.Ramani
#	29-Jan-2021
#
#	Statistical process Control chart . Key concepts - Target , Upper and Lower control limits , upper and lower spec limits
#	Stochastic process control - This is for a continuous process. The idea is that normal random variations will result in observations that hop around target - higher and lower
#	If a 7 point trend is observed (higher or lower), corrective action should be take to break the trend
#	Control limit violations and Spec violations will need corrective action anyway. 
#       The goal is to flag following conditions 
#	Seven point trend - does not cross center line for 7 successive observations. 
#       7 th point and on should be flagged.
#	Arbitrary decision - if first reading is exactly on target treat it as high trend. 
#       Classification states are SV,CV and OK
#       Upper trend goes 1,2,3,4. Lower trend goes -1,-2,-3, -4
#	
#	This script take 1 parameter - the name of the csv file 
#	Later on , we can make this event driven - we can add a single observation and see the new plot
#
#
#
#	Some observations on the script  - This is my second python script !   This is not robust - no error handling !
#	The first results tag should show an asterisk - I think ! Not debugging that ! 
#
#       Bad practice - lazy about # for every line
"""
	Sample input format - Needed columns
Serial,Static
1,2
2,2
3,2
4,2
5,4
6,2
7,4
8,3
9,3
10,3
...
96,4
97,1.9
98,4.1
99,6
100,0.9

"""

##

import sys

# The approach to take is that we reset consecutive points only when center line is crossed
# all points in a trend 7 or greater will have to be flagged - generate an alert 
# control or spec violation becomes immediately visible as there are control and spec lines on the chart 

def	classify_observation(val, prev_classification , trend_length):


#	if trending was in low direction , the new value has to be above target to reset 
	if	trend_length < 0:
		if	val > target: 
			trend_length = 1
		else:
			trend_length = trend_length -1
	else: # trend was not negative before 
		if	val < target:
			trend_length = - 1
		else:
			trend_length = trend_length + 1	
		
	


#	flag control ans spec  violations
	if val > upper_spec or val < lower_spec :
		classification = "SV"
	elif	val > upper_control or val < lower_control:
		classification = "CV"	
	
	elif	trend_length >= 7 or trend_length <= -7 :
		classification = "TV"	
	else:
		classification = "OK"



#	print("lcl " , lower_control , " " , classification , " trend_length ", trend_length)
	return classification , trend_length



# import pandas module 
import csv
import pandas as pd 

#define global variables

# in a real scenario , we would load this from somewhere

target = 3
upper_control = 4
lower_control = 2
lower_spec = 1
upper_spec = 5

  
# creating a data frame from csv file
df = pd.read_csv("spctxt.csv") 
# print(df.head()) 

#
# initialize variables
#
trend_length = 0
classification = "first"
val = 3

# will process each row - call classify_observation
# will store the 2 results in an array - add as columns at the end and write out to disk
# I do see that row by row processing is slow - didn't know how to pass the results of last call to the next
# will figure out optimizing later - idea - running total features ?

classification_arr = []  # start collecting classifications
Trend_length_array=  [] # start collecting trend count for each value


for ind in df.index:
	result = classify_observation(df['Static'][ind] , classification, trend_length)
#	print("ind " , ind , " val " , df['Static'][ind] , " trend_length ", trend_length , " result " , result)
	classification_arr.append(result[0])
	Trend_length_array.append(result[1])
	trend_length = result[1]
#
#	Add the 2 new columns and write out.
#

df['classification']= classification_arr 
df['trend_length']= Trend_length_array

df.to_csv (r'spctxt_processed.csv', index = False, header=True)


import numpy as np
import matplotlib.pyplot as plt

fig, ax = plt.subplots()


plt.title('7 Point trend and Limit Violations - SPC Sample', color="tab:orange" , fontweight='bold')

plt.xlabel('Observation Number' ,color="tab:orange" , fontweight='bold')
plt.ylabel('Observed Value' ,color="tab:orange" , fontweight='bold')

#
#	Set up the 5 lines
#
ax.axhline(linewidth=0.5, color='#d62728')
# Horizontal line at y=target that spans the xrange.
ax.axhline(y= target,color="green" , label='Target')

ax.axhline(y= upper_control,color="tab:orange",label='Upper and Lower Control')


ax.axhline(y= lower_control,color="tab:orange")

ax.axhline(y= upper_spec,color="tab:red",label='Upper and Lower Spec')


ax.axhline(y= lower_spec,color="tab:red")

#
#	Plot the input with + markers
#

plt.plot(df["Serial"], df["Static"], 'b',ls='-' , linewidth=0.75 , marker=".")

# do only trend violations and plot only if there is data . Use orange upward triangle
#
trenddf = df.loc[ (df['trend_length'] >= 7) | (df['trend_length'] <= -7) ]

if	len(trenddf.index) > 0 :
	plt.scatter(trenddf["Serial"], trenddf["Static"], c="tab:orange" , marker="X" , s=20*2**3) 

# do only control limit violations and plot If there is data 
#
cvdf = df.loc[ (df['classification'] == 'CV')]

if	len(cvdf.index) > 0 :
	plt.scatter(cvdf["Serial"], cvdf["Static"], c="tab:orange" , marker="s" , s=20*2**3)

# do only spec violations and plot If there is data 
#
specdf = df.loc[ (df['classification'] == 'SV')]

if	len(specdf.index) > 0 :
	plt.scatter(specdf["Serial"], specdf["Static"], c="tab:red" , marker="s" , s=20*2**3)
plt.legend()

#
#	Save the output graph
#
plt.savefig('SPCsampleplot.png',orientation='landscape')
plt.savefig('SPCsampleplot.pdf',orientation='landscape')
plt.show()

