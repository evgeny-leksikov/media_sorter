# Copyright (c) 2016-2017, Evgeny Leksikov evgeny.leksikov@gmail.com
# 
# This is free and unencumbered software released into the public domain.
# 
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
# 
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
# 
# For more information, please refer to <http://unlicense.org/>


__author__ = "Evgeny Leksikov"
__date__ = "$Sep 15, 2016 9:46:23 AM$"

import datetime
import os
import subprocess
import shutil
import time

from optparse import OptionParser

def is_video_file(fpath):
    FPATH = fpath.upper()
    return FPATH.endswith("MTS") or \
        FPATH.endswith("MP4") or \
        FPATH.endswith("MOV") or \
        FPATH.endswith("AVI")

def is_photo_file(fpath):
    FPATH = fpath.upper()
    return FPATH.endswith("PNG") or FPATH.endswith("JPG")

def is_media_file(fpath, ftype):
    FPATH = fpath.upper()
    if os.path.isfile(fpath) and \
        (("SYNOPHOTO_THUMB" not in fpath) and \
        ("SYNOPHOTO_FILM" not in fpath) and \
        ("@EADIR" not in fpath)):

        if ftype == 'photo':
            return is_photo_file(fpath)
        elif ftype == 'video':
            return is_video_file(fpath)
        elif ftype == 'all':
            return is_photo_file(fpath) or is_video_file(fpath)
    return False

def walk_dir(dir_path, f_type):

    foo_all_list = [ os.path.join(dir_path, i) for i in os.listdir(dir_path) ]

    ret_list = [ f for f in foo_all_list if is_media_file(f, f_type) ]
    
    foo_d_list = [ d for d in foo_all_list if os.path.isdir(d) ]
    for d in foo_d_list:
        if "@EADIR" not in d.upper():
            ret_list.extend(walk_dir(d, f_type))

    return ret_list

def gen_dst_dir_path(f):
    (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(f)
    t = min(time.gmtime(mtime), time.gmtime(ctime))
    dsep = '.'
    ret = str(t.tm_year) + os.path.sep + \
          str(t.tm_year) + dsep + ("0" if t.tm_mon < 10 else "") + str(t.tm_mon) + dsep +\
          ("0" if t.tm_mday < 10 else "") + str(t.tm_mday)
    return ret

def gen_dst_file_path(src, dst):
    fname = os.path.basename(src)
    dst_full_path = os.path.join(dst, fname)
	
    i = 0
    while os.path.exists(dst_full_path):
        dst_full_path = os.path.join(dst, str() + \
        ("00" if i < 100 else "0" if i < 10 else "") + str(i) + fname)
    return dst_full_path

def gen_log_name():
    return "photo_sorting_d" + \
        datetime.datetime.now().isoformat().lower().replace(':', '-').replace('.', '-') + \
        ".log"

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-i", "--input",  help = "input directory to pick up madia files, "\
        "log file in format \"media_sorting_d<date>t<time>.log\" will be created here")
    parser.add_option("-o", "--output", help = "output directory to put sorted media library")
    parser.add_option("-t", "--type", help = "type of files: \"photo\", \"video\" or \"all\"")
    (options, args) = parser.parse_args()

    if not (os.path.isdir(options.input) and os.path.isdir(options.output)):
        print "Wrong parameters"
        parser.print_help()
        exit(1)

    with open(os.path.join(options.input, gen_log_name()), 'a') as log_file:

        f_list = walk_dir(options.input, options.type)

        for f in f_list:
            dst = os.path.join(options.output, gen_dst_dir_path(f))
            try:
                if not (os.path.exists(dst) and os.path.isdir(dst)):
                    os.makedirs(dst)
                dst_file = gen_dst_file_path(f, dst)

                subprocess.call( [ 'synoindex', '-d', f ] )
                print >> log_file, "moving ", f, " to ", dst_file
                shutil.move(f, dst_file)
                subprocess.call( [ 'synoindex', '-a', dst_file ] )
            except Exception, e:
                print >> log_file, "error: ", str(e)
        print >> log_file, "done"

    exit(0)
