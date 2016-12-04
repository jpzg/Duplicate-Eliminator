# coding: utf-8
# Python 2.7
# 3/10/16
# Attempt 2, I really don't want to bother debugging the previous one
# Goes through all subdirectories and hashes parts of any file over the size limit to identify duplicates
# When a duplicate is found, press 1 or 2 to delete one of them, or n to leave both.

import hashlib
import threading
import os
import time

time.clock()
mode = raw_input("Enter mode: (normal/prompt)")

def ver():
    return "v1.0.5?"

def hash_file(path): # Might have issues with small files
    m = hashlib.md5()
    f = open(path,'rb')
    m.update(f.read(65535)) # read some data from the start of the file
    f.seek(int(os.path.getsize(path)/2)) # read more from the middle
    m.update(f.read(65535))
    f.seek(65535,2)         # read more from the end
    m.update(f.read(65535))
    f.close()
    return m.digest()

def search_data(hash, array): # Find the index to insert a hash
    start = 0
    end = len(array)
    while end - start > 1:
        mid = int((start+end)/2)
        result = greater(hash,array[mid][0])
        if result == 1:
            start = mid
        elif result == 0:
            end = mid
        elif result == -1:
            return mid,array[mid][1]
    if start == end:
        return start, None
    result = greater(hash, array[start][0]) # that index could be wrong
    if result == -1:
        return start, array[start][1]
    elif result == 0:
        return start, None
    elif result == 1:
        return end, None
    
def greater(b1, b2): # Compare bytestrings byte-by-byte. Returns 1 if 1 is greater, 0 if 2 is greater, and -1 if equal.
    for e in range(0,len(b1) if len(b1) <= len(b2) else len(b2)): # Ternary operator. Use the length of the shorter one.
        if b1[e] > b2[e]:
            return 1
        elif b1[e] < b2[e]:
            return 0
    if len(b1) < len(b2):
        return 0
    elif len(b1) > len(b2):
        return 1
    return -1
    
def main():
    hash_data = []
    l = open("log.txt",'w')
    count = 0

    for dirpath, dirnames, fnames in os.walk(os.getcwd()):
    	if dirpath == os.getcwd():
        	del dirnames[dirnames.index("Library")]
        	del dirnames[dirnames.index(".Trash")] # Don't look in either of these
        matched_count = 0 
        for f in fnames:
            abs_path = "%s/%s" % (dirpath,f) # changed from \\ for mac compatibility
            try:
                if os.path.getsize(abs_path) < 1000000: # Skip files smaller than 1MB
                    continue
            except Exception: # This once threw a PermissionError somehow
                continue
            try:
                hash = hash_file(abs_path)
                count += 1
                #print(abs_path)
            except IOError:
                print("IOError")
                continue
            except UnicodeEncodeError:
                print("error while printing")
            index, path = search_data(hash,hash_data)
            if path:
                if mode == "prompt":
                    print('Matched. Enter number to delete, or n to keep both:\n1. %s\n 2. %s' % (path,abs_path))
                    while True:
                        i = raw_input()
                        if i == '1':
                            os.remove(path)
            	            break
            	        if i == '2':
            	            os.remove(abs_path)
            	            break
            	        if i == 'n':
            	            try:
                                matched_count+=1
                                #print("MATCH:\n%s\n%s\n" % (path,abs_path))
                                l.write("MATCH:\n%s\n%s\n" % (path,abs_path))
                            except UnicodeEncodeError:
                                print("error while printing")
            	            break
            	        print('Invalid input')
            	else:
            	    try:
                        matched_count+=1
                        #print("MATCH:\n%s\n%s\n" % (path,abs_path))
                        l.write("MATCH:\n%s\n%s\n" % (path,abs_path))
                    except UnicodeEncodeError:
                        print("error while printing")
            elif index == len(hash_data):
                hash_data.append((hash,abs_path))
            else:
                hash_data.insert(index,(hash,abs_path))
        if len(fnames) == matched_count and matched_count != 0:
            print("%s" % dirpath)
            l.write("\n###\n\nALL FILES IN FOLDER MATCH\nSUBFOLDERS MAY CONTAIN UNIQUE ITEMS\n%s\n\n###\n\n\n" % dirpath)
    l.close()
    print("Hashed %s files in %s seconds" % (count,time.clock()))

main()

# tests
'''
assert greater(b'\x10',b'\x01') == 1
assert greater(b'\x01',b'\x10') == 0
assert greater(b'\x00',b'\x00') == -1
assert greater(b'\x00\x01',b'\x00\x02') == 0

assert search_data(b'\x00',[]) == 0
assert search_data(b'\x10',[(b'\x00')]) == 1
'''
