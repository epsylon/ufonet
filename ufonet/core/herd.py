#!/usr/bin/env python 
# -*- coding: utf-8 -*-"
"""
UFONet - DDoS attacks via Web Abuse - 2013/2014/2015 - by psy (epsylon@riseup.net)

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
from options import UFONetOptions
import threading, logging, datetime
import zombie

def set_options(self, options):
    self.options = options

def create_options(self, args=None):
    self.optionParser = UFONetOptions()
    self.options = self.optionParser.get_options(args)
    if not self.options:
        return False
    return self.options

# zombie tracking class
class Herd(object):
    # basic constructor
    def __init__(self):
        super(Herd, self).__init__()
        self.reset()
        self.total_connections=0
        self.total_hits=0
        self.total_fails=0
        self.total_time=0
        self.total_size=0
        self.total_connection_fails=0
        self.living=threading.active_count()
        self.stats={}

    # property setup
    def reset(self):
        self.active = []
        self.done = []
        self.lock = threading.Lock()
        self.result={}
        self.connection={}

    # got a new one !
    def new_zombie(self, zombie):
        self.total_connections+=1
        if zombie not in self.stats:
            self.stats[zombie]=[]
        with self.lock:
            self.active.append(zombie)

    # give me your report & byebye
    def kill_zombie(self, zombie, result,connection_failed):
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
        options = create_options(UFONetOptions)
        #print "Total invocations:", self.total_connections,"| Zombies:", len(self.stats),"| Hits:", self.total_hits,"| Fails:", self.total_fails
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

    # show what we have
    def dump(self):
        if self.total_connections==0:
            print "No herd without zombies"
            return
        if len(self.stats)==0:
            print "No statistics available"
            return
        max_fails=0
        max_failz=""
        max_hits=0
        max_hitz=""
        print '='*42
        print "Herd statistics"
        print "="*42
        for zombie_stat in self.stats:
            zs=self.stats[zombie_stat]
            hits=0
            fails=0
            retries=0
            time=0
            max_time=0
            min_time=zs[0][1]
            avg_time=0
            size=0
            max_size=0
            min_size=zs[0][2]
            avg_size=0
            for line in zs:
                if line[0]==200:
                    hits+=1
                else:
                    fails+=1
                if self.connection[zombie_stat]:
                    retries+=1
                time+=line[1]
                if line[1]>max_time: 
                    max_time=line[1]
                if line[1]<min_time: 
                    min_time=line[1]
                size+=line[2]
                if line[2]>max_size: 
                    max_size=line[2]
                if line[2]<min_size: 
                    min_size=line[2]
            min_time = str(datetime.timedelta(seconds=min_time))
            avg_time = str(datetime.timedelta(seconds=time/len(zs)))
            max_time = str(datetime.timedelta(seconds=max_time))
            time = str(datetime.timedelta(seconds=time))
            min_size = self.sizeof_fmt(int(min_size))
            avg_size = self.sizeof_fmt(int(size/len(zs)))
            max_size = self.sizeof_fmt(int(max_size))
            size=self.sizeof_fmt(int(size))
            print 'Zombie :', zombie_stat, " | ", hits, " hits ", fails ," fails ", retries, " retries "
            print "  Times:", time, " total ", min_time, " min ", avg_time ," avg ", max_time, " max "
            print "  Sizes:", size, " total ", min_size, " min ", size ," avg ", max_size, " max "
            print "-"*21
            if fails > max_fails:
                max_fails = fails
                max_failz = zombie_stat
            if hits > max_hits:
                max_hits = hits
                max_hitz = zombie_stat
        if max_hits > 0:
            print "="*80
            print "Zombie 0day: ", max_hitz, " with ", max_hits, " hits"
        if max_fails > 0:
            print "="*80
            print "Worst zombie: ", max_failz, " with ", max_fails, " fails"
        print "="*80
        print "\n"
        print "Total invocations:", self.total_connections,"| Zombies:", len(self.stats),"| Hits:", self.total_hits,"| Fails:", self.total_fails
        total_time =  str(datetime.timedelta(seconds=self.total_time))
        avg_time_calc = self.total_time/self.total_connections
        avg_time = str(datetime.timedelta(seconds=avg_time_calc))
        print "Total time:", total_time, "| Avg time:", avg_time
        print "Total size:", self.sizeof_fmt(int(self.total_size)),"| Avg size:", self.sizeof_fmt(int(self.total_size/self.total_connections))
