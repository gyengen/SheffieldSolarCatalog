import os
import drms
import datetime
import urllib.request

def get_sharp(date):

    i = 0

    while True:

        try:
            ## Creating download folder with variable name
            now =  datetime.datetime.now()
            datefile = str(now.year) + '-' + str(now.month) + '-' + str(now.day) + '-' + str(now.hour) + 'h'

            # Creating Download directory if it does not exist
            out_dir = os.path.join('data/SRS_Sharp/', 'sharp_%s' % datefile)
            if not os.path.exists(out_dir):
              os.makedirs(out_dir)

            # Series - Can use either hmi.sharp_cea_720s or 'hmi.sharp_cea_720s_nrt'
            series = 'hmi.sharp_cea_720s_nrt'

            interval = '10m@10m'


            # query_string used to search for file
            # Want query_string to look like 'hmi.sharp_cea_720s_nrt[]2018.05.06_TAI/1d@10m'
            search_string = series + '[]' + '[' + date + '_TAI/' + interval +']'
            # Use 'as-is' instead of 'fits' if record keywords are not needed in the
            # FITS header. Reduces the server load!
            export_protocol = 'fits'
            #export_protocol = 'as-is'

            # Email is needed to log in to system
            email = 'vinhvu1995@gmail.com'

            # Log in to DRMS client
            c = drms.Client(verbose=True)
            #print(c.pkeys(r'hmi.sharp_720s'))
            #r = c.export(qstr, method='url', protocol=export_protocol, emimport sunpy.map

            r = c.export(search_string + '{bitmap}', method='url', protocol='fits', email=email)

            # Download selected files.
            print('\nRequest URL: %s' % r.request_url)
            print('%d file(s) available for download.\n' % len(r.urls))

            k = r.download(out_dir)

            location = list(k['download'])

            return location
            break
            # Sharp downloaded files plus location

            # sharp_table (filenames,out_dir)
        except urllib.error.URLError:
            print ("urllib.error.URLError has occurred /n SHARP download has failed.",)
            location = False
            return location
            break
            
        except drms.error.DrmsExportError:
            if i == 3:
                print ("Server is not working - Breaking")
                break
            else:
                print ("DrmsExportError - Maybe server is not working? Trying again")
                continue
