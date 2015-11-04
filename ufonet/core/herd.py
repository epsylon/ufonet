#!/usr/bin/env python 
# -*- coding: utf-8 -*-"
"""
UFONet - DDoS Botnet via Web Abuse - 2013/2014/2015 - by psy (epsylon@riseup.net)

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import socket, threading, logging, datetime
import zombie
import sys, os, re
from urlparse import urlparse

# zombie tracking class
class Herd(object):
    # basic constructor
    def __init__(self,ufonet):
        super(Herd, self).__init__()
        self.ufonet=ufonet
        self.reset()
        self.total_connections=0
        self.total_hits=0
        self.total_fails=0
        self.total_time=0
        self.total_size=0
        self.total_connection_fails=0
        self.living=threading.active_count()
        self.stats={}
        self.zombies_ready = []

    # property setup
    def reset(self):
        self.active = []
        self.done = []
        self.lock = threading.Lock()
        self.result={}
        self.connection={}

    # clean temporary statistic files
    def cleanup(self):
        try:
            if os.path.exists("/tmp/ufonet.html"):
                os.remove("/tmp/ufonet.html")
            if os.path.exists("/tmp/ufonet.html.tmp"):
                os.remove("/tmp/ufonet.html.tmp")
        except:
            pass

    # got a new one !
    def new_zombie(self, zombie):
        self.total_connections+=1
        if zombie not in self.stats:
            self.stats[zombie]=[]
        with self.lock:
            self.active.append(zombie)

    # give me your report & byebye
    def kill_zombie(self, zombie, result, connection_failed):
        with self.lock:
            try:
                self.result[zombie]=str(result)
                self.connection[zombie]=connection_failed
                self.done.append(zombie)
                if result[0]==200 :
                    self.total_hits+=1
                else:
                    self.total_fails+=1
                if connection_failed:
                    self.total_connection_fails+=1
                self.active.remove(zombie)
                self.total_time+=result[1]
                self.total_size+=result[2]
                if zombie in self.stats:
                    self.stats[zombie].append(result)
                else:
                    pass
            except:
                pass

    # head count (+/- headless zombies)
    # active thread count = 1 principal + 1/zombie
    def no_more_zombies(self):
        ac=threading.active_count()
        options = self.ufonet.options
        if options.verbose == True:
            if ac>self.living:
                print "[Control] Active zombies:", ac-self.living, ", waiting for them to return..."
            else:
                print "="*41
                print "\n[Control] All zombies returned to the master ;-)"
                print "-"*21
        with self.lock:
            return ac==self.living

    # retrieve result by zombie name
    def get_result(self,zombie):
        return  self.result[zombie] or False

    # retrieve connection status by zombie name
    def connection_failed(self,zombie):
        return  self.connection[zombie] or False

    # retrieve size on correct format
    def sizeof_fmt(self, size, suffix='B'):
        for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
            if abs(size) < 1024.0:
                return "%3.1f%s%s" % (size, unit, suffix)
            size /= 1024.0
        return "%.1f%s%s" % (size, 'Yi', suffix)

    # generate html statistics
    def dump_html(self,final=False):
        buf=""
        out=self.get_stat()
        if os.path.exists("/tmp/ufonet.html.tmp"):
            print 'tmp file found, html output abort 2 !!!'
            return
        buf += "<div>" + os.linesep
        if out['err'] is not None:
            buf += "<div>Errors : <br/>"+str(out['err'])+'</div>'+os.linesep
        buf += "<h2>Conn: " +str(self.total_connections)+" - Zombies: "+str(len(self.stats))+" - Hits: "+str(self.total_hits)+" - Fails: "+str(self.total_fails)+"</h2>"+os.linesep
        buf += "<div id='zombie_list'><h3>Zombies: </h3>"
        if len(out['data'])==0:
            buf += "waiting..."
        for l in out["data"] :
            hits='<font color="green">'+str(out['data'][l]['hits'])+'</font>'
            fails=str(out['data'][l]['fails'])
            buf += "<button href='#' title='"+l+"' onclick=\"zombie_detail("+str(out['data'][l])+")\">"+fails+"/"+hits+"</button>"+os.linesep
        buf += "</div>"
        if out['max_hits'] > 0:
            buf += "<hr/>"+os.linesep
            buf += "<div>Zombie 0day: "+str( out['max_hitz'])+ " with "+str( out['max_hits'])+ " hits</div>"+os.linesep
        if out['max_fails'] > 0:
            buf += "<hr/>"+os.linesep
            buf += "<div>Worst zombie: "+str(out['max_failz'])+ " with "+str(out['max_fails'])+" fails</div>"+os.linesep
        buf += "<hr/>"+os.linesep
        buf += "<div>Total time:" +str(out['total_time'])+ " | Avg time:"+str(out['avg_time'])+"</div>"+os.linesep
        buf += "<div>Total size:"+str(out['total_size'])+" | Avg size:"+str(out['avg_size'])+"</div>"+os.linesep
        f = open("/tmp/ufonet.html.tmp", "w") 
        f.write(buf)
        if(final):
            f.write("<script>hdone=true</script>")
        f.close()
        os.rename("/tmp/ufonet.html.tmp","/tmp/ufonet.html")

    # generate statistics for stdout
    def format(self, out):
        print '='*42
        print "Herd statistics"
        print "="*42
        if len(out['data'])==0:
            print "waiting..."
            return
        for zo in out['data']:
            z=out['data'][zo]
            print 'Zombie :', z['name'], " | ", z['hits'], " hits ", z['fails'] ," fails ", z['retries'], " retries "
            print "  Times:", z['time'], " total ", z['min_time'], " min ", z['avg_time'] ," avg ", z['max_time'], " max "
            print "  Sizes:", z['size'], " total ", z['min_size'], " min ", z['size'] ," avg ", z['max_size'], " max "
            print "-"*21
        if out['max_hits'] > 0:
            print "="*80
            print "Zombie 0day: ", out['max_hitz'], " with ", out['max_hits'], " hits"
        if out['max_fails'] > 0:
            print "="*80
            print "Worst zombie: ", out['max_failz'], " with ", out['max_fails'], " fails"
        print "="*80
        print "Total invocations:", self.total_connections,"| Zombies:", len(self.stats),"| Hits:", self.total_hits,"| Fails:", self.total_fails
        print "Total time:", out['total_time'], "| Avg time:", out['avg_time']
        print "Total size:", out['total_size'],"| Avg size:", out['avg_size']

    # show what we have
    def get_stat(self):
        data={}
        out={'err':None,"header":"","data":{},"total":{},"footer":"",'max_fails':0,'max_failz':"",'max_hits':0,'max_hitz':""}
        if os.path.exists("html.tmp"):
            out['err']= "tmp file found"
            return out
        if self.total_connections==0:
            out['err']= "No herd without zombies"
            return out
        if len(self.stats)==0:
            out['err']=  "No statistics available"
            return out
        self.zero_fails = 0
        for zombie_stat in self.stats:
            zs=self.stats[zombie_stat]
            entry={'name':zombie_stat,"hits":0,"fails":0,"retries":0,"time":0,"max_time":0,"min_time":zs[0][1],"avg_time":0,"size":0,"max_size":0,"min_size":zs[0][2],"avg_size":0}
            if len(zs)==0:
                continue
            for line in zs:
                if line[0]==200:
                    entry['hits']+=1
                else:
                    entry['fails']+=1
                if self.connection[zombie_stat]:
                    entry['retries']+=1
                entry['time']+=line[1]
                if line[1]>entry['max_time']: 
                    entry['max_time']=line[1]
                if line[1]<entry['min_time']: 
                    entry['min_time']=line[1]
                entry['size']+=line[2]
                if line[2]>entry['max_size']: 
                    entry['max_size']=line[2]
                if line[2]<entry['min_size']: 
                    entry['min_size']=line[2]
            if entry['fails'] == 0:
                self.zero_fails +=1
            entry['min_time'] = str(datetime.timedelta(seconds=entry['min_time']))
            entry['avg_time'] = str(datetime.timedelta(seconds=entry['time']/len(zs)))
            entry['max_time'] = str(datetime.timedelta(seconds=entry['max_time']))
            entry['time'] = str(datetime.timedelta(seconds=entry['time']))
            entry['min_size'] = self.sizeof_fmt(int(entry['min_size']))
            entry['avg_size'] = self.sizeof_fmt(int(entry['size']/len(zs)))
            entry['max_size'] = self.sizeof_fmt(int(entry['max_size']))
            entry['size']=self.sizeof_fmt(int(entry['size']))
            if entry['fails'] > out['max_fails']:
                out['max_fails'] = entry['fails']
                out['max_failz'] = zombie_stat
            if entry['hits'] > out['max_hits']:
                out['max_hits'] = entry['hits']
                out['max_hitz'] = zombie_stat
            if entry['fails'] == 0:
                if zombie_stat not in self.zombies_ready: # parse for repetitions
                    self.zombies_ready.append(zombie_stat)
            data[entry['name']] = entry
        out['total_time'] =  str(datetime.timedelta(seconds=self.total_time))
        out['avg_time_calc'] = self.total_time/self.total_connections
        out['avg_time'] = str(datetime.timedelta(seconds=out['avg_time_calc']))
        out['total_size'] = self.sizeof_fmt(int(self.total_size))
        out['avg_size'] = self.sizeof_fmt(int(self.total_size/self.total_connections))
        out['data']=data
        return out

    # wrapper
    def dump(self):
        out=self.get_stat()
        if out['err'] is not None:
            print "[ERR] "+out['err']
        self.format(out)

    def list_fails(self):
        options = self.ufonet.options
        if self.total_connections==0:
            return
        if self.zombies_ready == None: # if not herd return
            return
        if not options.forceyes:
            print '-'*25
            update_reply = raw_input("Wanna update your army (Y/n)")
            print '-'*25
        else:
            update_reply = "Y"
        if update_reply == "n" or update_reply == "N":
            print "\nBye!\n"
            return
        else:
            self.ufonet.update_zombies(self.zombies_ready)
            print "\n[INFO] - Botnet updated! ;-)\n"
        if os.path.exists('mothership') == True:
            os.remove('mothership') # remove mothership stream
        if os.path.exists('alien') == True:
            os.remove('alien') # remove random alien worker
