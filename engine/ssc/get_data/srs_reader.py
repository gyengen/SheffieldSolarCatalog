from astropy.table import Table, Column
import numpy as np

def cord_split_b(x):
	if x[0]=='N': return int(x[1:3])
	if x[0]=='S': return -1*int(x[1:3])

def cord_split_l(x):
	if x[3]=='W': return int(x[4:6])
	if x[3]=='E': return -1*int(x[4:6])
	
def read_srs(fname):
	'''
	SRS file reader. Joint USAF/NOAA Solar Region Summary.
	Prepared jointly by the U.S. Dept. of Commerce, NOAA, Space Weather Prediction Center and the U.S. Air Force.

	Parameters
	----------

	Returns
	-------
	'''

	active_regions=[]
	t = Table(names=('Nmbr', 'Location', 'Lo', 'Area', 'Z', 'LL', 'NN', 'Mag_Type'),
			  dtype=('S6', 'S6', 'i4', 'i4', 'S3', 'i4', 'i4', 'S10'))
	with open(fname) as f:content = f.readlines()
	for i in range(0,len(content)):
		if len(content[i][:].split()) == 8 and content[i][:].split()[0].isdigit():
			t.add_row(content[i][:].split())
		if len(content[i][:].split()) == 3 and content[i][:].split()[0].isdigit() and len(content[i][:].split()[1]) == 3:
			buff = content[i][:].split()
			buff.extend([0, 'N/A', 0, 1, 'Return'])
			buff[1] = buff[1] + 'E90'
			t.add_row(buff)
	buff = Column(map(cord_split_b, t['Location']), name='B', dtype=('i4'))
	t.add_column(buff, index=2)
	buff = Column(map(cord_split_l, t['Location']), name='Lcm', dtype=('i4'))
	t.add_column(buff, index=3)
	return t
	
