__author__ = 'mike'
from urllib2 import Request, urlopen, URLError
import json
import math
import sys
import os
import socket
import optparse
from multiprocessing import Pool

def arg_parser():
    cwd_dir = os.getcwd()
    parser = optparse.OptionParser()
    parser.add_option( '-r', dest='runid', help='Run ID: required')
    parser.add_option( '-a', dest='accesstoken', help='Access Token: required')
    ( options, args ) = parser.parse_args()

    try:
       if options.runid == None:
             raise Exception
       if options.accesstoken == None:
         raise Exception

    except Exception:
        print("Usage: BaseSpaceRunDownloader_v2.py -r <RunID> -a <AccessToken>")
        sys.exit()

    return options

def restrequest(rawrequest):
    request = Request(rawrequest)

    try:
        response = urlopen(request)
        json_string = response.read()
        json_obj = json.loads(json_string)

    except URLError, e:
        print 'Got an error code:', e
        sys.exit()

    return json_obj

def downloadrestrequest((rawrequest,path)):
    print 'downloading %s' % path
    dirname = RunID + os.sep + os.path.dirname(path)

    if dirname != '':
        if not os.path.isdir(dirname):
            os.makedirs(dirname)

    request = (rawrequest)

    outfile = open(RunID + os.sep + path,'wb')

    try:
        response = urlopen(request, timeout=1)
        outfile.write(response.read())
        outfile.close()

    except URLError, e:
        print 'Got an error code:', e
        outfile.close()
        downloadrestrequest((rawrequest, path))

    except socket.error:
        print 'Got a socket error: retrying'
        outfile.close()
        downloadrestrequest((rawrequest, path))


options = arg_parser()
RunID = options.runid
AccessToken = options.accesstoken

def oragnisefiles(index):
    offset = 1000*index
    hrefpath = []
    request = 'http://api.basespace.illumina.com/v1pre3/runs/%s/files?access_token=%s&limit=1000&Offset=%s' %(RunID ,AccessToken ,offset)
    json_obj = restrequest(request)
    nfiles = len(json_obj['Response']['Items'])
    for fileindex in range(nfiles):
        href = json_obj['Response']['Items'][fileindex]['Href']
        path = json_obj['Response']['Items'][fileindex]['Path']
        # pathstr += path + "\n"
        if "xml" in path and "log" not in path or "bcl" in path or "csv" in path:
            # hreflist.append(href)
            # pathlist.append(path)
            href = 'http://api.basespace.illumina.com/%s/content?access_token=%s' % (href, AccessToken)
            hrefpath.append((href, path))
    return hrefpath

def pooldownload((href, path)):
    request = 'http://api.basespace.illumina.com/%s/content?access_token=%s' % (href, AccessToken)
    print 'downloading %s' % path
    downloadrestrequest(request, path)

if __name__ == '__main__':
    import time
    start = time.time()
    pool = Pool(processes=10)
    RunID = options.runid
    AccessToken = options.accesstoken

    request = 'http://api.basespace.illumina.com/v1pre3/runs/%s/files?access_token=%s' % (RunID, AccessToken)

    json_obj = restrequest(request)
    totalCount = json_obj['Response']['TotalCount']

    noffsets = int(math.ceil(float(totalCount)/1000.0))
    hrefpath = pool.map(oragnisefiles, range(noffsets))
    for foldertup in hrefpath:
        pool.map(downloadrestrequest, foldertup)

    print time.time() - start

    # p.map(downloadrestrequest, (range(len(hreflist)),hreflist, pathlist, AccessToken))

    # for index in range(len(hreflist)):
    #
    #     request = 'http://api.basespace.illumina.com/%s/content?access_token=%s'%(hreflist[index],AccessToken)
    #     print 'downloading %s' %(pathlist[index])

        # downloadrestrequest(request, pathlist[index])
    # open("dir.txt", 'w').write(pathstr)