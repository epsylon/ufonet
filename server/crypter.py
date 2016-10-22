#!/usr/bin/env python 
# -*- coding: utf-8 -*-"
"""
UFONet - DDoS Botnet via Web Abuse - 2013/2014/2015/2016 - by psy (epsylon@riseup.net)

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
################################################################### 
# Code extracted from project: AnonTwi (anontwi.03c8.net)
###################################################################

KEY_SIZE = 32
BLOCK_SIZE = 16
MAC_SIZE = 20

from os import urandom
from hashlib import sha1, sha256
from Crypto.Cipher import AES
from base64 import b64encode, b64decode

trans_5C = "".join([chr (x ^ 0x5c) for x in xrange(256)])
trans_36 = "".join([chr (x ^ 0x36) for x in xrange(256)])

def hmac_sha1(key, msg):
    if len(key) > 20:
        key = sha1(key).digest()
    key += chr(0) * (20 - len(key))
    o_key_pad = key.translate(trans_5C)
    i_key_pad = key.translate(trans_36)
    return sha1(o_key_pad + sha1(i_key_pad + msg).digest()).digest()

def derive_keys(key):
    h = sha256()
    h.update(key)
    h.update('cipher')
    cipher_key = h.digest()
    h = sha256()
    h.update(key)
    h.update('mac')
    mac_key = h.digest()
    return (cipher_key, mac_key)

def generate_key():
    return b64encode(urandom(KEY_SIZE))

class Cipher(object):
    def __init__(self, key="", text=""):
        self.block_size = 16
        self.mac_size = 20
        self.key = self.set_key(key)
        self.text = self.set_text(text)
        self.mode = AES.MODE_CFB
  
    def set_key(self, key):
        try:
            key = b64decode(key)
        except TypeError:
            raise ValueError
        self.key = key
        return self.key

    def set_text(self, text):
        self.text = text 
        return self.text

    def encrypt(self):
        if BLOCK_SIZE + len(self.text) + MAC_SIZE > 105:
            self.text = self.text[:105 - BLOCK_SIZE - MAC_SIZE]
        (cipher_key, mac_key) = derive_keys(self.key)
        iv = urandom(BLOCK_SIZE)
        aes = AES.new(cipher_key, self.mode, iv)
        ciphertext = aes.encrypt(self.text)
        mac = hmac_sha1(mac_key, iv + ciphertext)
        return b64encode(iv + ciphertext + mac)

    def decrypt(self):
        try:
            iv_ciphertext_mac = b64decode(self.text)
        except TypeError:
            return None
        iv = iv_ciphertext_mac[:BLOCK_SIZE]
        ciphertext = iv_ciphertext_mac[BLOCK_SIZE:-MAC_SIZE]
        mac = iv_ciphertext_mac[-MAC_SIZE:]
        (cipher_key, mac_key) = derive_keys(self.key)
        expected_mac = hmac_sha1(mac_key, iv + ciphertext)
        if mac != expected_mac:
            return None
        aes = AES.new(cipher_key, self.mode, iv)
        return aes.decrypt(ciphertext)

if __name__ == "__main__":
    print "\nUFONet Crypter (AES256+HMAC-SHA1) -> (140 plain text chars = 69 encrypted chars)\n"
    text = str(raw_input("- Enter text: "))
    input_key = str(raw_input("- Enter key: "))
    key = b64encode(input_key)
    c = Cipher(key, text)
    msg = c.encrypt()
    c.set_text(msg)
    print '\n-> Ciphertext: [', msg, ']'
    print '\nLength:', len(msg)
    print '\n-> Key (share it using SNEAKNET!):', input_key
    print '\nDecryption PoC:', c.decrypt(), "\n"
