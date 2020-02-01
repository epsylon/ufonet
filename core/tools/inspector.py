#!/usr/bin/env python3 
# -*- coding: utf-8 -*-"
"""
This file is part of the UFONet project, https://ufonet.03c8.net

Copyright (c) 2013/2020 | psy <epsylon@riseup.net>

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import ssl, random, re
import urllib.request, urllib.error
from urllib.parse import urlparse as urlparse

# Inspector spidering class
class Inspector(object):
    def __init__(self,ufonet):
        self.ufonet=ufonet
        # set initial counters for objets
        self.c_images = 0 
        self.c_mov = 0
        self.c_webm = 0
        self.c_avi = 0
        self.c_swf = 0
        self.c_mpg = 0
        self.c_mpeg = 0
        self.c_mp3 = 0
        self.c_ogg = 0
        self.c_ogv = 0 
        self.c_wmv = 0
        self.c_css = 0
        self.c_js = 0
        self.c_xml = 0 
        self.c_php = 0
        self.c_html = 0
        self.c_jsp = 0
        self.c_asp = 0
        self.c_txt = 0
        self.ctx = ssl.create_default_context() # creating context to bypass SSL cert validation (black magic)
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE

    def proxy_transport(self, proxy):
        proxy_url = self.ufonet.extract_proxy(proxy)
        proxy = urllib.request.ProxyHandler({'https': proxy_url})
        opener = urllib.request.build_opener(proxy)
        urllib.request.install_opener(opener)

    def inspecting(self, target):
        # inspect HTML target's components sizes (ex: http://target.com/foo)           
        # [images, .mov, .webm, .avi, .swf, .mpg, .mpeg, .mp3, .ogg, .ogv, 
        # .wmv, .css, .js, .xml, .php, .html, .jsp, .asp, .txt]         
        biggest_files = {}
        if target.endswith(""):
            target.replace("", "/")
        self.ufonet.user_agent = random.choice(self.ufonet.agents).strip() # shuffle user-agent
        headers = {'User-Agent' : self.ufonet.user_agent, 'Referer' : self.ufonet.referer} # set fake user-agent and referer
        try:
            if self.ufonet.options.proxy: # set proxy
                self.proxy_transport(self.ufonet.options.proxy)
                req = urllib.request.Request(target, None, headers)
                target_reply = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
            else:
                req = urllib.request.Request(target, None, headers)
                target_reply = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
        except: 
            print('[Error] [AI] Unable to connect to target -> [Exiting!]\n')
            return
        try: # search for image files
            regex_img = []
            regex_img1 = "<img src='(.+?)'" # search on target's results using regex with simple quotation
            regex_img.append(regex_img1)
            regex_img2 = '<img src="(.+?)"' # search on target's results using regex with double quotation
            regex_img.append(regex_img2)
            #regex_img3 = '<img src=(.+?)>' # search on target's results using regex without quotations
            #regex_img.append(regex_img3)
            for regimg in regex_img:
                pattern_img = re.compile(regimg)
                img_links = re.findall(pattern_img, target_reply)
            imgs = {}
            for img in img_links:
                if self.ufonet.options.proxy: # set proxy
                    self.proxy_transport(self.ufonet.options.proxy)
                self.ufonet.user_agent = random.choice(self.ufonet.agents).strip() # shuffle user-agent
                headers = {'User-Agent' : self.ufonet.user_agent, 'Referer' : self.ufonet.referer} # set fake user-agent and referer
                try:
                    if img.startswith('http'):
                        size = 0
                    else:
                        target_host = urlparse(target)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        if img.startswith("data:image"):
                            size = 0
                        else:
                            if img.startswith('/'):
                                img = img.replace("/", "", 1)
                            try:
                                if self.ufonet.options.proxy: # set proxy
                                    self.proxy_transport(self.ufonet.options.proxy)
                                    req = urllib.request.Request(target_url + img, None, headers)
                                    img_file = urllib.request.urlopen(req, context=self.ctx).read()
                                else:
                                    req = urllib.request.Request(target_url + img, None, headers)
                                    img_file = urllib.request.urlopen(req, context=self.ctx).read()
                                print('+Image found: ' + target_url + img.split('"')[0])
                                size = len(img_file)
                                print('(Size: ' + str(size) + ' Bytes)')
                                imgs[img] = int(size)
                                self.c_images = self.c_images + 1
                                print('-'*12)
                            except:
                                size = 0
                except: 
                    print('[Error] [AI] Unable to retrieve info from Image -> [Discarding!]')
                    size = 0
            biggest_image = max(list(imgs.keys()), key=lambda x: imgs[x]) # search/extract biggest image value from dict
            if biggest_image:
                biggest_files[biggest_image] = imgs[biggest_image] # add biggest image to list
        except: # if not any image found, go for next
            pass
        try: # search for .mov files
            regex_mov = []
            regex_mov1 = "<a href='(.+?.mov)'" # search on target's results using regex with simple quotation
            regex_mov.append(regex_mov1)
            regex_mov2 = '<a href="(.+?.mov)"' # search on target's results using regex with double quotation
            regex_mov.append(regex_mov2)
            #regex_mov3 = '<a href=(.+?.mov)' # search on target's results using regex without quotations
            #regex_mov.append(regex_mov3)
            for regmov in regex_mov:
                pattern_mov = re.compile(regmov)
                mov_links = re.findall(pattern_mov, target_reply)
            movs = {}
            for mov in mov_links:
                try:
                    if mov.startswith('http'):
                        size = 0
                    else:
                        target_host = urlparse(target)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        try:
                            if self.ufonet.options.proxy: # set proxy
                                self.proxy_transport(self.ufonet.options.proxy)
                                req = urllib.request.Request(target_url + mov, None, headers)
                                mov_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            else:                    
                                req = urllib.request.Request(target_url + mov, None, headers)
                                mov_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            print('+Video (.mov) found: ' + target_url + mov.split('"')[0])
                            size = len(mov_file)
                            movs[mov] = int(size)
                            print('(Size: ' + str(size) + ' Bytes)')
                            self.c_mov = self.c_mov + 1
                            print('-'*12)
                        except:
                            size = 0
                except: 
                    print('[Error] [AI] Unable to retrieve info from Video -> [Discarding!]')
                    size = 0
            biggest_mov = max(list(movs.keys()), key=lambda x: movs[x]) # search/extract biggest video (.mov) value from dict
            if biggest_mov:
                biggest_files[biggest_mov] = movs[biggest_mov] # add biggest video (.mov) to list
        except: # if not any .mov found, go for next
            pass 
        try: # search for .webm files
            regex_webm = []
            regex_webm1 = "<a href='(.+?.webm)'" # search on target's results using regex with simple quotation
            regex_webm.append(regex_webm1)
            regex_webm2 = '<a href="(.+?.webm)"' # search on target's results using regex with double quotation
            regex_webm.append(regex_webm2)
            #regex_webm3 = '<a href=(.+?.webm)' # search on target's results using regex without quotations
            #regex_webm.append(regex_webm3)
            for regwebm in regex_webm:
                pattern_webm = re.compile(regwebm)
                webm_links = re.findall(pattern_webm, target_reply)
            webms = {}
            for webm in webm_links:
                try:
                    if webm.startswith('http'):
                        size = 0
                    else:
                        target_host = urlparse(target)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        try:
                            if self.ufonet.options.proxy: # set proxy
                                self.proxy_transport(self.ufonet.options.proxy)
                                req = urllib.request.Request(target_url + webm, None, headers)
                                webm_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            else:                    
                                req = urllib.request.Request(target_url + webm, None, headers)
                                webm_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            print('+Video (.webm) found: ' + target_url + webm.split('"')[0])
                            size = len(webm_file)
                            webms[webm] = int(size)
                            print('(Size: ' + str(size) + ' Bytes)')
                            self.c_webm = self.c_webm + 1
                            print('-'*12)
                        except:
                            size = 0
                except: 
                    print('[Error] [AI] Unable to retrieve info from Video -> [Discarding!]')
                    size = 0
            biggest_webm = max(list(webms.keys()), key=lambda x: webms[x]) # search/extract biggest video (.webm) value from dict
            if biggest_webm:
                biggest_files[biggest_webm] = webms[biggest_webm] # add biggest video (.webm) to list
        except: # if not any .webm found, go for next
            pass 
        try: # search for .avi files
            regex_avi = []
            regex_avi1 = "<a href='(.+?.avi)'" # search on target's results using regex with simple quotation
            regex_avi.append(regex_avi1)
            regex_avi2 = '<a href="(.+?.avi)"' # search on target's results using regex with double quotation
            regex_avi.append(regex_avi2)
            #regex_avi3 = '<a href=(.+?.avi)' # search on target's results using regex without quotations
            #regex_avi.append(regex_avi3)
            for regavi in regex_avi:
                pattern_avi = re.compile(regavi)
                avi_links = re.findall(pattern_avi, target_reply)
            avis = {}
            for avi in avi_links:
                try:
                    if avi.startswith('http'):
                        size = 0
                    else:
                        target_host = urlparse(target)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        try:
                            if self.ufonet.options.proxy: # set proxy
                                self.proxy_transport(self.ufonet.options.proxy)
                                req = urllib.request.Request(target_url + avi, None, headers)
                                avi_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            else:                    
                                req = urllib.request.Request(target_url + avi, None, headers)
                                avi_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            print('+Video (.avi) found: ' + target_url + avi.split('"')[0])
                            size = len(avi_file)
                            avis[avi] = int(size)
                            print('(Size: ' + str(size) + ' Bytes)')
                            self.c_avi = self.c_avi + 1
                            print('-'*12)
                        except:
                            size = 0
                except: 
                    print('[Error] [AI] Unable to retrieve info from Video -> [Discarding!]')
                    size = 0
            biggest_avi = max(list(avis.keys()), key=lambda x: avis[x]) # search/extract biggest video (.avi) value from dict
            if biggest_avi:
                biggest_files[biggest_avi] = avis[biggest_avi] # add biggest video (.avi) to list
        except: # if not any .avi found, go for next
            pass
        try: # search for .swf files
            regex_swf = []
            regex_swf1 = "<value='(.+?.swf)'" # search on target's results using regex with simple quotation
            regex_swf.append(regex_swf1)
            regex_swf2 = '<value="(.+?.swf)"' # search on target's results using regex with double quotation
            regex_swf.append(regex_swf2)
            #regex_swf3 = '<value=(.+?.swf)' # search on target's results using regex without quotations
            #regex_swf.append(regex_swf3)
            for regswf in regex_swf:
                pattern_swf = re.compile(regswf)
                swf_links = re.findall(pattern_swf, target_reply)
            swfs = {}
            for swf in swf_links:
                try:
                    if swf.startswith('http'):
                        size = 0
                    else:
                        target_host = urlparse(target)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        try:
                            if self.ufonet.options.proxy: # set proxy
                                self.proxy_transport(self.ufonet.options.proxy)
                                req = urllib.request.Request(target_url + swf, None, headers)
                                swf_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            else:                    
                                req = urllib.request.Request(target_url + swf, None, headers)
                                swf_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            print('+Flash (.swf) found: ' + target_url + swf.split('"')[0])
                            size = len(swf_file)
                            swfs[swf] = int(size)
                            print('(Size: ' + str(size) + ' Bytes)')
                            self.c_swf = self.c_swf + 1
                            print('-'*12)
                        except:
                            size = 0   
                except: 
                    print('[Error] [AI] Unable to retrieve info from Flash -> [Discarding!]')
                    size = 0
            biggest_swf = max(list(swfs.keys()), key=lambda x: swfs[x]) # search/extract biggest flash (.swf) value from dict
            if biggest_swf:
                biggest_files[biggest_swf] = swfs[biggest_swf] # add biggest flash (.swf) to list
        except: # if not any .swf found, go for next
            pass
        try: # search for .mpg files
            regex_mpg = []
            regex_mpg1 = "<src='(.+?.mpg)'" # search on target's results using regex with simple quotation
            regex_mpg.append(regex_mpg1)
            regex_mpg2 = '<src="(.+?.mpg)"' # search on target's results using regex with double quotation
            regex_mpg.append(regex_mpg2)
            #regex_mpg3 = '<src=(.+?.mpg)' # search on target's results using regex without quotations
            #regex_mpg.append(regex_mpg3)
            for regmpg in regex_mpg:
                pattern_mpg = re.compile(regmpg)
                mpg_links = re.findall(pattern_mpg, target_reply)
            mpgs = {}
            for mpg in mpg_links:
                try:
                    if mpg.startswith('http'):
                        size = 0
                    else:
                        target_host = urlparse(target)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        try:
                            if self.ufonet.options.proxy: # set proxy
                                self.proxy_transport(self.ufonet.options.proxy)
                                req = urllib.request.Request(target_url + mpg, None, headers)
                                mpg_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            else:                    
                                req = urllib.request.Request(target_url + mpg, None, headers)
                                mpg_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            print('+Video (.mpg) found: ' + target_url + mpg.split('"')[0])
                            size = len(mpg_file)
                            mpgs[mpg] = int(size)
                            print('(Size: ' + str(size) + ' Bytes)')
                            self.c_mpg = self.c_mpg + 1
                            print('-'*12)
                        except:
                            size = 0
                except: 
                    print('[Error] [AI] Unable to retrieve info from Video -> [Discarding!]')
                    size = 0
            biggest_mpg = max(list(mpgs.keys()), key=lambda x: mpgs[x]) # search/extract biggest video (.mpg) value from dict
            if biggest_mpg:
                biggest_files[biggest_mpg] = mpgs[biggest_mpg] # add biggest video (.mpg) to list
        except: # if not any .mpg found, go for next
            pass
        try: # search for .mpeg files
            regex_mpeg = []
            regex_mpeg1 = "<src='(.+?.mpeg)'" # search on target's results using regex with simple quotation
            regex_mpeg.append(regex_mpeg1)
            regex_mpeg2 = '<src="(.+?.mpeg)"' # search on target's results using regex with double quotation
            regex_mpeg.append(regex_mpeg2)
            #regex_mpeg3 = '<src=(.+?.mpeg)' # search on target's results using regex without quotations
            #regex_mpeg.append(regex_mpeg3)
            for regmpeg in regex_mpeg:
                pattern_mpeg = re.compile(regmpeg)
                mpeg_links = re.findall(pattern_mpeg, target_reply)
            mpegs = {}
            for mpeg in mpeg_links:
                try:
                    if mpeg.startswith('http'):
                        size = 0
                    else:
                        target_host = urlparse(target)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        try:
                            if self.ufonet.options.proxy: # set proxy
                                self.proxy_transport(self.ufonet.options.proxy)
                                req = urllib.request.Request(target_url + mpeg, None, headers)
                                mpeg_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            else:                    
                                req = urllib.request.Request(target_url + mpeg, None, headers)
                                mpeg_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            print('+Video (.mpeg) found: ' + target_url + mpeg.split('"')[0])
                            size = len(mpeg_file)
                            mpegs[mpeg] = int(size)
                            print('(Size: ' + str(size) + ' Bytes)')
                            self.c_mpeg = self.c_mpeg + 1
                            print('-'*12)
                        except:
                            size = 0
                except: 
                    print('[Error] [AI] Unable to retrieve info from Video -> [Discarding!]')
                    size = 0
            biggest_mpeg = max(list(mpegs.keys()), key=lambda x: mpegs[x]) # search/extract biggest video (.mpeg) value from dict
            if biggest_mpeg:
                biggest_files[biggest_mpeg] = mpegs[biggest_mpeg] # add biggest video (.mpeg) to list
        except: # if not any .mpeg found, go for next
            pass
        try: # search for .mp3 files
            regex_mp3 = []
            regex_mp31 = "<src='(.+?.mp3)'" # search on target's results using regex with simple quotation
            regex_mp3.append(regex_mp31)
            regex_mp32 = '<src="(.+?.mp3)"' # search on target's results using regex with double quotation
            regex_mp3.append(regex_mp32)
            #regex_mp33 = '<src=(.+?.mp3)' # search on target's results using regex without quotations
            #regex_mp3.append(regex_mp33)
            for regmp3 in regex_mp3:
                pattern_mp3 = re.compile(regmp3)
                mp3_links = re.findall(pattern_mp3, target_reply)
            mp3s = {}
            for mp3 in mp3_links:
                try:
                    if mp3.startswith('http'):
                        size = 0
                    else:
                        target_host = urlparse(target)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        try:
                            if self.ufonet.options.proxy: # set proxy
                                self.proxy_transport(self.ufonet.options.proxy)
                                req = urllib.request.Request(target_url + mp3, None, headers)
                                mp3_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            else:                    
                                req = urllib.request.Request(target_url + mp3, None, headers)
                                mp3_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            print('+Audio (.mp3) found: ' + target_url + mp3.split('"')[0])
                            size = len(mp3_file)
                            mp3s[mp3] = int(size)
                            print('(Size: ' + str(size) + ' Bytes)')
                            self.c_mp3 = self.c_mp3 + 1
                            print('-'*12)
                        except:
                            size = 0
                except: 
                    print('[Error] [AI] Unable to retrieve info from Audio -> [Discarding!]')
                    size = 0
            biggest_mp3 = max(list(mp3s.keys()), key=lambda x: mp3s[x]) # search/extract biggest audio (.mp3) value from dict
            if biggest_mp3:
                biggest_files[biggest_mp3] = mp3s[biggest_mp3] # add biggest audio (.mp3) to list
        except: # if not any .mp3 found, go for next
            pass
        try: # search for .mp4 files
            regex_mp4 = []
            regex_mp41 = "<src='(.+?.mp4)'" # search on target's results using regex with simple quotation
            regex_mp4.append(regex_mp41)
            regex_mp42 = '<src="(.+?.mp4)"' # search on target's results using regex with double quotation
            regex_mp4.append(regex_mp42)
            #regex_mp43 = '<src=(.+?.mp4)' # search on target's results using regex without quotations
            #regex_mp4.append(regex_mp43)
            for regmp4 in regex_mp4:
                pattern_mp4 = re.compile(regmp4)
                mp4_links = re.findall(pattern_mp4, target_reply)
            mp4s = {}
            for mp4 in mp4_links:
                try:
                    if mp4.startswith('http'):
                        size = 0
                    else:
                        target_host = urlparse(target)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        try:
                            if self.ufonet.options.proxy: # set proxy
                                self.proxy_transport(self.ufonet.options.proxy)
                                req = urllib.request.Request(target_url + mp4, None, headers)
                                mp4_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            else:                    
                                req = urllib.request.Request(target_url + mp4, None, headers)
                                mp4_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            print('+Video (.mp4) found: ' + target_url + mp4.split('"')[0])
                            size = len(mp4_file)
                            mp4s[mp4] = int(size)
                            print('(Size: ' + str(size) + ' Bytes)')
                            self.c_mp4 = self.c_mp4 + 1
                            print('-'*12)
                        except:
                            size = 0
                except: 
                    print('[Error] [AI] Unable to retrieve info from Video -> [Discarding!]')
                    size = 0
            biggest_mp4 = max(list(mp4s.keys()), key=lambda x: mp4s[x]) # search/extract biggest video (.mp4) value from dict
            if biggest_mp4:
                biggest_files[biggest_mp4] = mp4s[biggest_mp4] # add biggest video (.mp4) to list
        except: # if not any .mp4 found, go for next
            pass
        try: # search for .ogg files
            regex_ogg = []
            regex_ogg1 = "<src='(.+?.ogg)'" # search on target's results using regex with simple quotation
            regex_ogg.append(regex_ogg1)
            regex_ogg2 = '<src="(.+?.ogg)"' # search on target's results using regex with double quotation
            regex_ogg.append(regex_ogg2)
            #regex_ogg3 = '<src=(.+?.ogg)' # search on target's results using regex without quotations
            #regex_ogg.append(regex_ogg3)
            for regogg in regex_ogg:
                pattern_ogg = re.compile(regogg)
                ogg_links = re.findall(pattern_ogg, target_reply)
            oggs = {}
            for ogg in ogg_links:
                try:
                    if ogg.startswith('http'):
                        size = 0
                    else:
                        target_host = urlparse(target)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        try:
                            if self.ufonet.options.proxy: # set proxy
                                self.proxy_transport(self.ufonet.options.proxy)
                                req = urllib.request.Request(target_url + ogg, None, headers)
                                ogg_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            else:                    
                                req = urllib.request.Request(target_url + ogg, None, headers)
                                ogg_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            print('+Audio (.ogg) found: ' + target_url + ogg.split('"')[0])
                            size = len(ogg_file)
                            oggs[ogg] = int(size)
                            print('(Size: ' + str(size) + ' Bytes)')
                            self.c_ogg = self.c_ogg + 1
                            print('-'*12)
                        except:
                            size = 0
                except: 
                    print('[Error] [AI] Unable to retrieve info from Audio -> [Discarding!]')
                    size = 0
            biggest_ogg = max(list(oggs.keys()), key=lambda x: oggs[x]) # search/extract biggest video (.ogg) value from dict
            if biggest_ogg:
                biggest_files[biggest_ogg] = oggs[biggest_ogg] # add biggest video (.ogg) to list
        except: # if not any .ogg found, go for next
            pass
        try: # search for .ogv files
            regex_ogv = []
            regex_ogv1 = "<src='(.+?.ogv)'" # search on target's results using regex with simple quotation
            regex_ogv.append(regex_ogv1)
            regex_ogv2 = '<src="(.+?.ogv)"' # search on target's results using regex with double quotation
            regex_ogv.append(regex_ogv2)
            #regex_ogv3 = '<src=(.+?.ogv)' # search on target's results using regex without quotations
            #regex_ogv.append(regex_ogv3)
            for regogv in regex_ogv:
                pattern_ogv = re.compile(regogv)
                ogv_links = re.findall(pattern_ogv, target_reply)
            ogvs = {}
            for ogv in ogv_links:
                try:
                    if ogv.startswith('http'):
                        size = 0
                    else:
                        target_host = urlparse(target)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        try:
                            if self.ufonet.options.proxy: # set proxy
                                self.proxy_transport(self.ufonet.options.proxy)
                                req = urllib.request.Request(target_url + ogv, None, headers)
                                ogv_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            else:                    
                                req = urllib.request.Request(target_url + ogv, None, headers)
                                ogv_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            print('+Video (.ogv) found: ' + target_url + ogv.split('"')[0])
                            size = len(ogv_file)
                            ogvs[ogv] = int(size)
                            print('(Size: ' + str(size) + ' Bytes)')
                            self.c_ogv = self.c_ogv + 1
                            print('-'*12)
                        except:
                            size = 0
                except: 
                    print('[Error] [AI] Unable to retrieve info from Video -> [Discarding!]')
                    size = 0
            biggest_ogv = max(list(ogvs.keys()), key=lambda x: ogvs[x]) # search/extract biggest video (.ogv) value from dict
            if biggest_ogv:
                biggest_files[biggest_ogv] = ogvs[biggest_ogv] # add biggest video (.ogv) to list
        except: # if not any .ogv found, go for next
            pass
        try: # search for .wmv files
            regex_wmv = []
            regex_wmv1 = "<src='(.+?.wmv)'" # search on target's results using regex with simple quotation
            regex_wmv.append(regex_wmv1)
            regex_wmv2 = '<src="(.+?.wmv)"' # search on target's results using regex with double quotation
            regex_wmv.append(regex_wmv2)
            #regex_wmv3 = '<src=(.+?.wmv)' # search on target's results using regex without quotations
            #regex_wmv.append(regex_wmv3)
            for regwmv in regex_wmv:
                pattern_wmv = re.compile(regwmv)
                wmv_links = re.findall(pattern_wmv, target_reply)
            wmvs = {}
            for wmv in wmv_links:
                try:
                    if wmv.startswith('http'):
                        size = 0
                    else:
                        target_host = urlparse(target)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        try:
                            if self.ufonet.options.proxy: # set proxy
                                self.proxy_transport(self.ufonet.options.proxy)
                                req = urllib.request.Request(target_url + wmv, None, headers)
                                wmv_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            else:                    
                                req = urllib.request.Request(target_url + wmv, None, headers)
                                wmv_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            print('+Video (.wmv) found: ' + target_url + wmv.split('"')[0])
                            size = len(wmv_file)
                            wmvs[wmv] = int(size)
                            print('(Size: ' + str(size) + ' Bytes)')
                            self.c_wmv = self.c_wmv + 1
                            print('-'*12)
                        except:
                            size = 0
                except: 
                    print('[Error] [AI] Unable to retrieve info from Video -> [Discarding!]')
                    size = 0
            biggest_wmv = max(list(wmvs.keys()), key=lambda x: wmvs[x]) # search/extract biggest video (.wmv) value from dict
            if biggest_wmv:
                biggest_files[biggest_wmv] = wmvs[biggest_wmv] # add biggest video (.wmv) to list
        except: # if not any .wmv found, go for next
            pass
        try: # search for .css files
            regex_css = []
            regex_css1 = "href='(.+?.css[^']*)'" # search on target's results using regex with simple quotation
            regex_css.append(regex_css1)
            regex_css2 = 'href="(.+?.css[^"]*)"' # search on target's results using regex with double quotation
            regex_css.append(regex_css2)
            #regex_css3 = "href=(.+?.css[^']*)" # search on target's results using regex without quotations
            #regex_css.append(regex_css3)
            for regcss in regex_css:
                pattern_css = re.compile(regcss)
                css_links = re.findall(pattern_css, target_reply)
            csss = {}
            for css in css_links:
                try:
                    if css.startswith('http'):
                        size = 0
                    else:
                        target_host = urlparse(target)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        if css.startswith("//"):
                            size = 0
                        elif "http://" in css or "https://" in css:
                            size = 0
                        else:
                            if css.startswith('/'):
                                css = css.replace("/", "", 1)
                            try:
                                if self.ufonet.options.proxy: # set proxy
                                    self.proxy_transport(self.ufonet.options.proxy)
                                    req = urllib.request.Request(target_url + css, None, headers)
                                    css_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                                else:                    
                                    req = urllib.request.Request(target_url + css, None, headers)
                                    css_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                                print('+Style (.css) found: ' + target_url + css.split('"')[0])
                                size = len(css_file)
                                csss[css] = int(size)
                                print('(Size: ' + str(size) + ' Bytes)')
                                self.c_css = self.c_css + 1
                                print('-'*12)
                            except:
                                size = 0
                except: 
                    print('[Error] [AI] Unable to retrieve info from Style -> [Discarding!]')
                    size = 0
            biggest_css = max(list(csss.keys()), key=lambda x: csss[x]) # search/extract biggest style (.css) value from dict
            if biggest_css:
                biggest_files[biggest_css] = csss[biggest_css] # add biggest style (.css) to list
        except: # if not any .css found, go for next
            pass
        try: # search for .js files
            regex_js = []
            regex_js1 = "src='(.+?.js[^']*)'" # search on target's results using regex with simple quotation
            regex_js.append(regex_js1)
            regex_js2 = 'src="(.+?.js[^"]*)"' # search on target's results using regex with double quotation
            regex_js.append(regex_js2)
            #regex_js3 = "src=(.+?.js[^']*)" # search on target's results using regex without quotations
            #regex_js.append(regex_js3)
            for regjs in regex_js:
                pattern_js = re.compile(regjs)
                js_links = re.findall(pattern_js, target_reply)
            jss = {}
            for js in js_links:
                try:
                    if js.startswith('http'):
                        size = 0
                    else:
                        target_host = urlparse(target)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        if js.startswith("//"):
                            size = 0
                        elif "http://" in js or "https://" in js:
                            size = 0
                        else:
                            if js.startswith('/'):
                                js = js.replace("/", "", 1)
                            print('+Script (.js) found: ' + target_url + js.split('"')[0])
                            if self.ufonet.options.proxy: # set proxy
                                self.proxy_transport(self.ufonet.options.proxy)
                                req = urllib.request.Request(target_url + js, None, headers)
                                js_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            else:                    
                                req = urllib.request.Request(target_url + js, None, headers)
                                js_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            size = len(js_file)
                            jss[js] = int(size)
                            print('(Size: ' + str(size) + ' Bytes)')
                            self.c_js = self.c_js + 1
                            print('-'*12)
                except: 
                    print('[Error] [AI] Unable to retrieve info from Script -> [Discarding!]')
                    size = 0
            biggest_js = max(list(jss.keys()), key=lambda x: jss[x]) # search/extract biggest script (.js) value from dict
            if biggest_js:
                biggest_files[biggest_js] = jss[biggest_js] # add biggest script (.js) to list
        except: # if not any .js found, go for next
            pass
        try: # search for .xml files
            regex_xml = []
            regex_xml1 = "href='(.+?.xml)'" # search on target's results using regex with simple quotation
            regex_xml.append(regex_xml1)
            regex_xml2 = 'href="(.+?.xml)"' # search on target's results using regex with double quotation
            regex_xml.append(regex_xml2)
            #regex_xml3 = 'href=(.+?.xml)' # search on target's results using regex without quotations
            #regex_xml.append(regex_xml3)
            for regxml in regex_xml:
                pattern_xml = re.compile(regxml)
                xml_links = re.findall(pattern_xml, target_reply)
            xmls = {}
            for xml in xml_links:
                try:
                    if xml.startswith('http'):
                        size = 0
                    else:
                        target_host = urlparse(target)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        try:
                            if self.ufonet.options.proxy: # set proxy
                                self.proxy_transport(self.ufonet.options.proxy)
                                req = urllib.request.Request(target_url + xml, None, headers)
                                xml_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            else:                    
                                req = urllib.request.Request(target_url + xml, None, headers)
                                xml_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            print('+Script (.xml) found: ' + target_url + xml).split('"')[0]
                            size = len(xml_file)
                            xmls[xml] = int(size)
                            print('(Size: ' + str(size) + ' Bytes)')
                            self.c_xml = self.c_xml + 1
                            print('-'*12)
                        except:
                            size = 0
                except: 
                    print('[Error] [AI] Unable to retrieve info from Script -> [Discarding!]')
                    size = 0
            biggest_xml = max(list(xmls.keys()), key=lambda x: xmls[x]) # search/extract biggest script (.xml) value from dict
            if biggest_xml:
                biggest_files[biggest_xml] = xmls[biggest_xml]  # add biggest script (.xml) to list
        except: # if not any .xml found, go for next
            pass
        try: # search for .php files
            regex_php = []
            regex_php1 = "href='(.+?.php)'" # search on target's results using regex with simple quotation
            regex_php.append(regex_php1)
            regex_php2 = 'href="(.+?.php)"' # search on target's results using regex with double quotation
            regex_php.append(regex_php2)
            #regex_php3 = 'href=(.+?.php)' # search on target's results using regex without quotations
            #regex_php.append(regex_php3)
            for regphp in regex_php:
                pattern_php = re.compile(regphp)
                php_links = re.findall(pattern_php, target_reply)
            phps = {}
            for php in php_links:
                try:
                    if php.startswith('http'):
                        size = 0
                    else:
                        target_host = urlparse(target)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        try:
                            if self.ufonet.options.proxy: # set proxy
                                self.proxy_transport(self.ufonet.options.proxy)
                                req = urllib.request.Request(target_url + php, None, headers)
                                php_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            else:                    
                                req = urllib.request.Request(target_url + php, None, headers)
                                php_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            print('+Webpage (.php) found: ' + target_url + php.split('"')[0])
                            size = len(php_file)
                            phps[php] = int(size)
                            print('(Size: ' + str(size) + ' Bytes)')
                            self.c_php = self.c_php + 1
                            print('-'*12)
                        except:
                            size = 0
                except: 
                    print('[Error] [AI] Unable to retrieve info from Webpage -> [Discarding!]')
                    size = 0
            biggest_php = max(list(phps.keys()), key=lambda x: phps[x]) # search/extract biggest file (.php) value from dict
            if biggest_php:
                biggest_files[biggest_php] = phps[biggest_php] # add biggest file (.php) to list
        except: # if not any .php found, go for next
            pass
        try: # search for .html files
            regex_html = []
            regex_html1 = "href='(.+?.html)'" # search on target's results using regex with simple quotation
            regex_html.append(regex_html1)
            regex_html2 = 'href="(.+?.html)"' # search on target's results using regex with double quotation
            regex_html.append(regex_html2)
            #regex_html3 = 'href=(.+?.html)' # search on target's results using regex without quotations
            #regex_html.append(regex_html3)
            for reghtml in regex_html:
                pattern_html = re.compile(reghtml)
                html_links = re.findall(pattern_html, target_reply)
            htmls = {}
            for html in html_links:
                try:
                    if html.startswith('http'):
                        size = 0
                    else:
                        target_host = urlparse(target)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        try:
                            if self.ufonet.options.proxy: # set proxy
                                self.proxy_transport(self.ufonet.options.proxy)
                                req = urllib.request.Request(target_url + html, None, headers)
                                html_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            else:                    
                                req = urllib.request.Request(target_url + html, None, headers)
                                html_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            print('+Webpage (.html) found: ' + target_url + html.split('"')[0])
                            size = len(html_file)
                            htmls[html] = int(size)
                            print('(Size: ' + str(size) + ' Bytes)')
                            self.c_html = self.c_html + 1
                            print('-'*12)
                        except:
                            size = 0
                except: 
                    print('[Error] [AI] Unable to retrieve info from Webpage -> [Discarding!]')
                    size = 0
            biggest_html = max(list(htmls.keys()), key=lambda x: htmls[x]) # search/extract biggest file (.html) value from dict
            if biggest_html:
                biggest_files[biggest_html] = htmls[biggest_html] # add biggest file (.html) to list
        except: # if not any .html found, go for next
            pass
        try: # search for .jsp files
            regex_jsp = []
            regex_jsp1 = "href='(.+?.jsp)'" # search on target's results using regex with simple quotation
            regex_jsp.append(regex_jsp1)
            regex_jsp2 = 'href="(.+?.jsp)"' # search on target's results using regex with double quotation
            regex_jsp.append(regex_jsp2)
            #regex_jsp3 = 'href=(.+?.jsp)' # search on target's results using regex without quotations
            #regex_jsp.append(regex_jsp3)
            for regjsp in regex_jsp:
                pattern_jsp = re.compile(regjsp)
                jsp_links = re.findall(pattern_jsp, target_reply)
            jsps = {}
            for jsp in jsp_links:
                try:
                    if jsp.startswith('http'):
                        size = 0 
                    else:
                        target_host = urlparse(target)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        try:
                            if self.ufonet.options.proxy: # set proxy
                                self.proxy_transport(self.ufonet.options.proxy)
                                req = urllib.request.Request(target_url + jsp, None, headers)
                                jsp_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            else:                    
                                req = urllib.request.Request(target_url + jsp, None, headers)
                                jsp_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            print('+Webpage (.jsp) found: ' + target_url + jsp.split('"')[0])
                            size = len(jsp_file)
                            jsps[jsp] = int(size)
                            print('(Size: ' + str(size) + ' Bytes)')
                            self.c_jsp = self.c_jsp + 1
                            print('-'*12)
                        except:
                            size = 0
                except: 
                    print('[Error] [AI] Unable to retrieve info from Webpage -> [Discarding!]')
                    size = 0
            biggest_jsp = max(list(jsps.keys()), key=lambda x: jsps[x]) # search/extract biggest file (.jsp) value from dict
            if biggest_jsp:
                biggest_files[biggest_jsp] = jsps[biggest_jsp] # add biggest file (.jsp) to list
        except: # if not any .jsp found, go for next
            pass
        try: # search for .asp files
            regex_asp = []
            regex_asp1 = "href='(.+?.asp)'" # search on target's results using regex with simple quotation
            regex_asp.append(regex_asp1)
            regex_asp2 = 'href="(.+?.asp)"' # search on target's results using regex with double quotation
            regex_asp.append(regex_asp2)
            #regex_asp3 = 'href=(.+?.asp)' # search on target's results using regex without quotations
            #regex_asp.append(regex_asp3)
            for regasp in regex_asp:
                pattern_asp = re.compile(regasp)
                asp_links = re.findall(pattern_asp, target_reply)
            asps = {}
            for asp in asp_links:
                try:
                    if asp.startswith('http'):
                        size = 0
                    else:
                        target_host = urlparse(target)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        try:
                            if self.ufonet.options.proxy: # set proxy
                                self.proxy_transport(self.ufonet.options.proxy)
                                req = urllib.request.Request(target_url + asp, None, headers)
                                asp_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            else:                    
                                req = urllib.request.Request(target_url + asp, None, headers)
                                asp_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            print('+Webpage (.asp) found: ' + target_url + asp.split('"')[0])
                            size = len(asp_file)
                            asps[asp] = int(size)
                            print('(Size: ' + str(size) + ' Bytes)')
                            self.c_asp = self.c_asp + 1
                            print('-'*12)
                        except:
                            size = 0
                except: 
                    print('[Error] [AI] Unable to retrieve info from Webpage -> [Discarding!]')
                    size = 0
            biggest_asp = max(list(asps.keys()), key=lambda x: asps[x]) # search/extract biggest file (.asp) value from dict
            if biggest_asp:
                biggest_files[biggest_asp] = asps[biggest_asp] # add biggest file (.asp) to list
        except: # if not any .asp found, go for next
            pass
        try: # search for .txt files
            regex_txt = []
            regex_txt1 = "href='(.+?.txt)'" # search on target's results using regex with simple quotation
            regex_txt.append(regex_txt1)
            regex_txt2 = 'href="(.+?.txt)"' # search on target's results using regex with double quotation
            regex_txt.append(regex_txt2)
            #regex_txt3 = 'href=(.+?.txt)' # search on target's results using regex without quotations
            #regex_txt.append(regex_txt3)
            for regtxt in regex_txt:
                pattern_txt = re.compile(regtxt)
                txt_links = re.findall(pattern_txt, target_reply)
            txts = {}
            for txt in txt_links:
                try:
                    if txt.startswith('http'):       
                        size = 0 
                    else:
                        target_host = urlparse(target)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        try:
                            if self.ufonet.options.proxy: # set proxy
                                self.proxy_transport(self.ufonet.options.proxy)
                                req = urllib.request.Request(target_url + txt, None, headers)
                                txt_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            else:                    
                                req = urllib.request.Request(target_url + txt, None, headers)
                                txt_file = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                            print('+File (.txt) found: ' + target_url + txt.split('"')[0])
                            size = len(txt_file)
                            txts[txt] = int(size)
                            print('(Size: ' + str(size) + ' Bytes)')
                            self.c_txt = self.c_txt + 1
                            print('-'*12)
                        except:
                            size = 0
                except: 
                    print('[Error] [AI] Unable to retrieve info from Text file -> [Discarding!]')
                    size = 0
            biggest_txt = max(list(txts.keys()), key=lambda x: txts[x]) # search/extract biggest file (.txt) value from dict
            if biggest_text:
                biggest_files[biggest_txt] = txts[biggest_txt] # add biggest file (.txt) to list
        except: # if not any .txt found, go for next
            pass
        print("\n" +'='*80)
        total_objects = self.c_images + self.c_mov + self.c_webm + self.c_avi + self.c_swf + self.c_mpg + self.c_mpeg + self.c_mp3 + self.c_ogg + self.c_ogv + self.c_wmv + self.c_css + self.c_js + self.c_xml + self.c_php +  self.c_html + self.c_jsp + self.c_asp + self.c_txt
        print("Total objects found:", total_objects)
        print('-'*20)
        print("images:", self.c_images)
        print(".mov  :", self.c_mov) 
        print(".jsp  :", self.c_jsp)
        print(".avi  :", self.c_avi)
        print(".html :", self.c_html)
        print(".mpg  :", self.c_mpg)
        print(".asp  :", self.c_asp)
        print(".mp3  :", self.c_mp3)
        print(".js   :", self.c_js)
        print(".ogv  :", self.c_ogv)
        print(".wmv  :", self.c_wmv)
        print(".css  :", self.c_css)
        print(".mpeg :", self.c_mpeg)
        print(".xml  :", self.c_xml)
        print(".php  :", self.c_php)
        print(".txt  :", self.c_txt)
        print(".webm :", self.c_webm)
        print(".ogg  :", self.c_ogg)
        print(".swf  :", self.c_swf)
        print('-'*20)
        print('='*80)
        if(biggest_files=={}):
            print("\n[Info] [AI] Not any link found on target! -> [Exiting!]\n\n")
            print('='*80 + '\n')
            return
        biggest_file_on_target = max(list(biggest_files.keys()), key=lambda x: biggest_files[x]) # search/extract biggest file value from dict
        target_host = urlparse(target)
        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
        if biggest_file_on_target.startswith('http'): # used for absolute links
            for url,size in list(biggest_files.items()): # review all dict values
                if url.startswith('http'):
                    if not target_url in url: # extract/dismiss external links         
                        del biggest_files[url] # remove value from dict
            biggest_file_on_target = max(list(biggest_files.keys()), key=lambda x: biggest_files[x]) # extract new value
            print('=Biggest File: ' + biggest_file_on_target)
        else: # used for relative links
            if not target_url.endswith('/'): # add "/" to end of target
                target_url = target_url + "/"
            print('=Biggest File: ' + target_url + biggest_file_on_target)
        print('='*80 + '\n')
