#pip install patool   < DO IT FIRST
# patool is kind of weird, on my windows box it finds and uses nanazip which is a 7zip fork. I don't know how it found it, and I don't care.

# clean up this garbage, copied from modmapper and don't need most of it
# anyway, imports and vars
import patoolib
import json
import io
import sys
import os
import re
import shutil
import subprocess
from os import listdir
from os.path import isfile, join


# where the archives are
zipfiles_folder = "D:\\Downloads\\zips"
# where unpack mods you want to match against the archives are
modmappermods_folder = "E:\\testmods"
# working directory where stuff can be unzipped, WILL BE DELETED
temp_dir = "E:\\modextract_temp"
# any non-nexus mods will be moved here
movefolder = "E:\\notnexus"
# esp/esm/owmaddon files will be moved here
espmovefolder = "E:\\testmods"

path = os.getcwd()
esplist = []
espdict = {}
nexuslinkdict = {}
inside_zip_list = ""
problem = False
moreinfo = False
unknownlist = []
unknowncounter = 0
failedlist = []
failcounter = 0
failedremove = 0
noespcounter = 0
noesplist = []
copyfaillist = []
movedcounter = 0
copyfailcounter = 0
noesp = False
nocopylist = ["grass","groundcover","aes","vurt"]
replacecharlist = [",","@","-"]
replacecharwith = "_"

# don't point to nexus for TR indev
trexcludelist = ["TR_Islands","TR_LakeAndaram","TR_OthEast","TR_Restexteriors","TR_Sundered_Scar"]
trexcludeurl = "https://www.tamriel-rebuilt.org/releasefiles"

# esps that I don't want on the map for whatever reason (in the cases below, they add cells VERY far from the center of the map)
espblocklist = ["Doom_Door_01.esp","C0N2 v1.01.esp"]
blockedfiles = 0
blockedfilelist = []
# create list of zips
ziplist = []
ziplist += [each for each in os.listdir(zipfiles_folder) if (each.lower().endswith('.zip') or each.lower().endswith('.rar') or each.lower().endswith('.7z'))]

# my live list of extracted mods, crazy filenames and all like "version 1.esp". 
modmappermodlist = []
modmappermodlist += [each for each in os.listdir(modmappermods_folder) if (each.lower().endswith('.esm') or each.lower().endswith('.esp') or each.lower().endswith('.omwaddon'))]

def findfile(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)
            
counter = 1
tempdirtemplate = temp_dir
filecounter = 1
totalfiles = len(ziplist)
# loop through collected archives


                            
                            
for zipfiles in ziplist:
    print("file",filecounter,"of",totalfiles,". unknown:",unknowncounter,"brokenarchive:",failcounter,"noesp:",noespcounter,"copyfail:",copyfailcounter,"blocklisted:",blockedfiles)
    filecounter+=1
    # does the temp folder exist? NUKE IT
    if os.path.isdir(temp_dir):
        try:
            shutil.rmtree(temp_dir)
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))
            problem = True
    # WHY THIS NONSENSE BELOW? Some people packed their mods complete with file ownership and perms in the archive. Can patool extract without those? Maybe, I don't know? Can I write code to reset perms on both windows and linux? It's tricky but maybe? Will cost
    #time though. Or I could just say fuck it, add a number at the end to create a new folder, and clean up manually after. I count 11 files out of ~2700 which have some kind of issue like that so it's pretty rare.
    if problem:
        temp_dir = tempdirtemplate + str(counter)
        counter += 1
        problem = False
    # (re)create temp folder
    try:
        os.mkdir(temp_dir)
    except Exception as e:
        print ("dir creation failed",repr(e))
        problem = True
    else:
        if moreinfo:
            print ("Successfully created the directory %s " % temp_dir)
    if problem:
        sys.exit()
    # extract files from archive to temp folder
    if not problem:
        if moreinfo:
            print("extracting",zipfiles)
        try:
            patoolib.extract_archive(zipfiles_folder+"\\"+zipfiles, outdir=temp_dir,verbosity=-1)
        except Exception as e:
            print("problem extracting",zipfiles,repr(e))
            failedlist.append(zipfiles)
            failcounter += 1
            problem = True
    # compare to list of esp/esm
    esplist = []
    if not problem:
        for folder, subfolders, files in os.walk(temp_dir):
            for espesmomw in files:
                if (espesmomw.lower().endswith('.esm') or espesmomw.lower().endswith('.esp') or espesmomw.lower().endswith('.omwaddon')):
                    espesmomwoutputfile = espesmomw
                    espblock = False
                    for blockthesefiles in espblocklist:
                        if blockthesefiles in espesmomw:
                            blockedfiles += 1
                            blockedfilelist.append(espesmomw)
                            print("blocklisted:",espesmomw)
                            espblock = True
                    for replacers in replacecharlist:
                        if replacers in espesmomw:
                            espesmomwoutputfile = espesmomwoutputfile.replace(replacers,"_")
                            print("name replace",espesmomw,"with",espesmomwoutputfile)
                    copytargetesp = findfile(espesmomw, temp_dir)
                    foldertargetesp = espmovefolder+"\\"+espesmomwoutputfile
                    #print(copytargetesp,"to",foldertargetesp)
                    goaheadcopy = True
                    for dontcopyme in nocopylist:
                        if dontcopyme in espesmomw:
                            goaheadcopy = False
                    if goaheadcopy and not espblock:
                        try:
                            shutil.copyfile(copytargetesp, foldertargetesp)
                        except:
                            copyfailcounter += 1
                            copyfaillist.append(espesmomwoutputfile)
                        esplist.append(espesmomwoutputfile)
        if not esplist:
            noesp = True
            print("noesp",zipfiles)
            noespcounter += 1
            noesplist.append(zipfiles)
            #shutil.copyfile(zipfiles_folder+"\\"+unzippedesp, dst)
        #espdict.update({zipfiles:esplist})
        espdict[zipfiles]=esplist
        print(zipfiles,"contained ",esplist)
        nexusmodlink = ""
        nexusmodlink2 = ""
        nexusmodname = ""
        mynexuslink = ""
        trexcludeflag = False
        for items in trexcludelist:
            if items in zipfiles:
                nexusmodlink = trexcludeurl
                trexcludeflag = True
        if not trexcludeflag:
            try:
                # nexusmodlink = re.findall('-.*?-', zipfiles)
                # nexusmodlink = int(nexusmodlink[0][1:-1])
                test = re.findall('[^0-9]+([0-9]+)', zipfiles)
                foundlink = False
                # so the nexusmodID in the filename is a great idea, but nothing stops mod authors from adding any amount of numbers to their file. Like "3E421, a story", or "housemod v1.233781".
                # plus when dealing with old games like MW and poking around in old mods, you're going to come across short numbers for the nexusmodsID.
                # anyway we're testing for xxxxx, then xxxx, then xxx number sequences in order.
                loops = 5
                while loops > 2:
                    if not foundlink:
                        for items in test:
                            if len(items) == loops:
                                print("match",items)
                                foundlink = True
                            if foundlink:
                                break
                    loops = loops-1
                if not foundlink:
                    items = ""
                if foundlink:
                    nexusmodlink = int(items)
            except:
                pass
            # try:
                # nexusmodlink2 = re.findall('-.*?\.', zipfiles)
                # nexusmodlink2 = int(nexusmodlink2[0][1:-1])
            # except:
                # pass
        found = False
        if nexusmodlink and not found and not trexcludeflag:
            print("nexus ID is hopefully https://www.nexusmods.com/morrowind/mods/"+str(nexusmodlink))
            mynexuslink = "https://www.nexusmods.com/morrowind/mods/"+str(nexusmodlink)
            found = True
            mynexuslink = nexusmodlink
        if nexusmodlink2 and not found and not trexcludeflag:
            print("nexus ID is hopefully https://www.nexusmods.com/morrowind/mods/"+str(nexusmodlink2))
            mynexuslink = "https://www.nexusmods.com/morrowind/mods/"+str(nexusmodlink2)
            found = True
        if trexcludeflag:
            mynexuslink = trexcludeurl
            found = True
        if found:
            nexusmodname = re.findall('.*?-', zipfiles)
            #print("suggested name:",nexusmodname[0][:-1])
            nexuslinkdict.update({zipfiles:mynexuslink})
        moved = False
        if not found and not moved:
            unknownlist.append(zipfiles)
            unknowncounter += 1
            moved = True
            print("not a nexus mod")
            try:
                shutil.move(zipfiles_folder+"\\"+zipfiles, movefolder+"\\"+zipfiles)
            except:
                pass
        if noesp and not moved:
            print("no esp found")
            moved = True
            try:
                shutil.move(zipfiles_folder+"\\"+zipfiles, movefolder+"\\"+zipfiles)
            except:
                pass
        moved = False
        esplist = []
        noesp = False
    # remove temp folder
    try:
        shutil.rmtree(temp_dir)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
        failedremove += 1
    problem = False
    noesp = False

############# that concludes the dict building.

########## dumb debug stuff
# print("---- dictionary:")
# print(espdict)
# print("---- nexus:")
# print(nexuslinkdict)
print(counter,"files had problems, enjoy cleaning up")
currentmodname = "TR_Mainland.esm"
# print("---------")
# print("going to look for",currentmodname)
#########################
#print(espdict)

###### example of a lookup

# testing
print("testing dict against:",currentmodname)
for allthezips in espdict:
    listofzipmods = espdict[allthezips]
    for individualmods in listofzipmods:
        if currentmodname in individualmods:
            print("the mod",currentmodname,"was found in",allthezips)
            if allthezips in nexuslinkdict.keys():
                print("nexusmodlink is", nexuslinkdict[allthezips])
# if currentmodname in espdict.values():
    # print("YAY")
    # findmod = list(espdict.keys())[list(espdict.values()).index(currentmodname)]
    # print("the mod",currentmodname,"was found in",findmod)
    # if findmod in nexuslinkdict.keys():
        # print("YAYx2")
        # print("nexusmodlink is ", nexuslinkdict[findmod])
    # else:
        # print("I have no link for this :(")
        
        
zipdict = open("zipdict.txt","w")
espdump = json.dumps(espdict)
zipdict.write(str(espdump))
zipdict.close()

linkdict = open("linkdict.txt","w")
nexusdump = json.dumps(nexuslinkdict)
linkdict.write(str(nexuslinkdict))
linkdict.close()

print("noesp:", noesplist)
print("failed:",failedlist)
print("unkown:",unknownlist)
print("copy fail:",copyfaillist)