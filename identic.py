import sys 
import os
from hashlib import sha256

typeC = False
typeN = False
typeS = False    
typeF = True

def main():
    dirList = []
    hashmapC = {}
    hashmapN = {}
    global typeC
    global typeN
    global typeS
    global typeF
    # reading arguments
    for ch in sys.argv[1:]:
        if ch.find('-') != -1:  # not directory, an option
            if ch.find('d') != -1:
                typeF = False
            if ch.find('c') != -1:
                typeC = True
            if ch.find('n') != -1:
                typeN = True
            if ch.find('s') != -1:
                typeS = True
        else:
            if not os.path.isabs(ch):  # just to be sure that given path is absolute
                ch = os.path.realpath(ch)
            dirList.append(ch)
    if not typeC and not typeN: 
    # when none of the -c and -n is given default is -c
        typeC = True 
    
    if len(dirList) == 0:
    # if no directories given default is working directory
        dirList.append(os.getcwd())
    # got the flags and directories
    sett = set(dirList) # to eliminate same paths and enhance performance:
    dirlist = (list(sett))
    for dir in dirlist:
        if typeN:
            get_hash_name(dir,hashmapN)
        if typeC:
            get_hash_content(dir,hashmapC)

    if typeN and typeC: #-cn
        hashmapCN = {}
        for every in hashmapN: #concat two hashes
            hashmapCN[every] = hashmapN[every] + hashmapC[every]
        print_identicals(hashmapCN)
    elif typeN and not typeC: #-n
        print_identicals(hashmapN)
    else: # -c
        print_identicals(hashmapC)

#  print function: takes duplicate files or dirs from given hashmap parameter then sorts it.
#  Finally prints sorted duplicates.
def print_identicals(hashmap):
    rev_map = {}

    for key, value in hashmap.items():
        rev_map.setdefault(value, set()).add(key)
    result = filter(lambda x: len(x) > 1, rev_map.values())
    # nonduplicate paths are filtered
    # since map consists of two sets, the result is a set but I need a list
    listofSets = list(result)
    liste = []
    #listofSets is list of all duplicates
    for sets in listofSets:
        liste.append(list(sets)) 
        
    for sublist in liste: # First sort all duplicate sets alphabetically in itself
        sublist.sort()
    if typeS and not (typeN and not typeC):  # -s is invalid when -n is given (-cs,-s,-cns situations)
        # If there is -s flag:
        # The duplicates should be printed in descending order of size(project description).
        # Please put tab(\t) after each filepath and add size of them.
        liste.sort(key=lambda liste: os.path.getsize(liste[0]), reverse=True)
    if not typeS: #(-n ,-c ,-cn situations)
        # If there is not -s flag:
        # The duplicates should be printed in sorted order, alphabetically.
        liste.sort()
    for sublist in liste:  # list of sets
        for element in sublist:  # set of identical files or dirs
            if typeS and not (typeN and not typeC) and element != None: 
               print(f"{element}\t {os.path.getsize(element)}")
            else:
                print(element)
        print()

# this function is called when -n option is given
# it works with both files and directories but since most of the function handles with dir, I named parameter as dir.
# if given parameter is file all it does is hashing tha files name.
# else given parameter is directory then given directory is whether empty or not.
#   if given directory is empty then simply hash its name.
#   else recursively call subdirs and subfiles and concat them to return final hash.
def get_hash_name(dir,hashmapN):
    # recursion base cases: file or empty dir
    f = sha256() # hash function
    if not os.path.isdir(dir):  # means file
        f.update(os.path.basename(dir).encode("utf-8"))
        if typeF:
            hashmapN[dir] = f.hexdigest()
        return f.hexdigest()
    else:  # means directory
        if len(os.listdir(dir)) == 0:  # means empty directory
            if (dir[-1] == "/" or dir[-1] == "\\"): # extract "/" from end of the dirs name
                dir = dir[:len(dir) - 1]
            f.update(os.path.basename(dir).encode("utf-8"))
            if not typeF:
                hashmapN[dir] = f.hexdigest()
            return f.hexdigest()
        else:
            if typeF: # -f
                # now I am in a directory and I have -f option so I should look my subdirs to find files to hash
                curlist = os.listdir(dir)
                for sub in curlist:
                    newsub = dir + "/" + sub
                    get_hash_name(newsub,hashmapN)
            else: # -d
                curlist = os.listdir(dir)
                subhasheslist = []
                for sub in curlist:
                    newsub = dir + "/" + sub
                    subhasheslist.append(get_hash_name(newsub,hashmapN))
                subhasheslist.sort()
                if (dir[-1] == "/" or dir[-1] == "\\"):
                    dir = dir[:len(dir) - 1]
                f.update(os.path.basename(dir).encode("utf-8"))
                f.update((f.hexdigest() + "" + "".join(subhasheslist)).encode("utf-8"))
                return f.hexdigest()

# same working principle with get_hash_name function but works with -c option.
# 
def get_hash_content(dir, hashmapC):
    # recursion base cases: file or empty dir
    f = sha256()
    if not os.path.isdir(dir):  # means file
        try: # maybe given dir path is not valid
            file = open(dir, "rb")
        except FileNotFoundError:
            print(f"path not found: {dir}")
            sys.exit() 

        s = file.read()
        f.update(s)
        if typeF:
            hashmapC[dir] = f.hexdigest()
        return f.hexdigest()
    else:  # means directory
        if len(os.listdir(dir)) == 0:  # means empty directory
            f.update(" ".encode("utf-8")) #I decided to take empty dirs hash as hash of 1 space:(" ") string
            if not typeF:
                hashmapC[dir] = f.hexdigest()
            return f.hexdigest()
        else:
            curlist = os.listdir(dir)
            subhasheslist = []
            for sub in curlist:
                newsub = dir + "/" + sub
                subhasheslist.append(get_hash_content(newsub,hashmapC))
            subhasheslist.sort()
            f.update("".join(subhasheslist).encode("utf-8"))
            if not typeF:
                hashmapC[dir] = f.hexdigest()
            return f.hexdigest()

if __name__== "__main__":
    main()

