from ftplib import FTP
import os


def ftp_srs(fname):
	'''Join to the NOAA server and download the requested SRS file

	Parameters
	----------
		fname - SRS information to download

	Returns
	-------
		error - bool'''

	error = 0
	link = 'ftp.swpc.noaa.gov'
	folder = '/pub/forecasts/SRS/'

	ftp = FTP(link)
	ftp.login()
	ftp.cwd(folder)  
	#ftp.retrlines('LIST')
	ftp.retrbinary('RETR '+fname, open(fname, 'wb').write)
	ftp.quit()
	
	return error
