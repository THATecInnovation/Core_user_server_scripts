#!/usr/bin/python
import csv
import os
from datetime import datetime
import sys
import hashlib
import urllib.request

verbose = False

class upd_info:
    Device = ""
    Compiled = "0"

    def get_attributes(self):
        attribs = []
        for attribute in upd_info.__dict__.keys():
            if attribute[:2] != '__':
                value = getattr(upd_info, attribute)
                if not callable(value):
                    attribs.append(attribute)
        return(attribs)

def load_online_modules():
    try:
        online_modules = []
        url = "https://www.thatec-innovation.com/Updates/Updates.csv"
        with urllib.request.urlopen(url) as file:
            content = file.read().decode(f'utf-8')
            content = str(content).splitlines()
            for line in content:
                online_modules.append(line.split(';')[0])
        return online_modules
    except Exception as err:
        print("Error loading online module list from thatec-innovation.com. Please make sure that no folder name in this directory is identical to any software module in the THATec Innovation device library!")
        print("Reported error: {}".format(err))
        return []

def get_existing_filelist(folder):
    if os.path.exists('./'+folder+'/filelist.csv'):
        try:
            with open('./'+folder+'/filelist.csv', 'r') as csv_file: 
                reader=csv.reader(csv_file, delimiter=";")
                return(list(filter(None,reader))) # remove empty elements
        except FileNotFoundError:
            return None
        except Exception as err:
            print("ERROR reading old filelist in module {}: {}".format(folder,err))
            sys.exit("Stopping execution")

def get_files_in_folder(folder): # Check all existing files in folder and create MD5 sums
    filelist_array=[] # array into which the filepaths and MD5 sums will be written
    upd_files = []
    for dirname, dirnames, filenames in os.walk(folder):
        for file in filenames:
            if file == "filelist.csv":# skip filelist.csv
                pass
            else: #create MD5 sum
                if str(file).endswith('.upd'): 
                    upd_files.append(file)
                hash_md5 = hashlib.md5()
                file_path = dirname + '\\' + file
                try:
                    with open(file_path, "rb") as file:
                        for chunk in iter(lambda: file.read(4096), b""):
                            hash_md5.update(chunk)
                    file_path = str.replace(file_path,folder+"\\","",1) # remove folder from path
                    filelist_array.append([file_path,'',hash_md5.hexdigest()]) # add path and hashsum into array
                except Exception as err:
                    print("ERROR reading MD5 sum from file {}: {}".format(file_path,err))
                    sys.exit("Stopping execution")
    upd_path = folder + "\\" + folder + ".upd"
    if len(upd_files) > 1:
        print("Multiple .upd files found in folder {}. Please delete files!".format(folder))
        sys.exit("Stopping execution")
    elif len(upd_files) == 1 and upd_path not in upd_files: #upd file at incorrect path => rename
        os.rename(folder + "\\" + upd_files[0],upd_path)
    return filelist_array

def get_deleted_filelist_and_updates (old_filelist, new_filelist):
    return_value = {
        "deleted_filelist" : [],
        "update" : False
    }
    for new_entry in new_filelist: # walk through new entries
        if new_entry not in old_filelist: # check for new files
            return_value["update"] = True
    for old_entry in old_filelist: # walk through old entries
        if old_entry[0] not in [row_new[0] for row_new in new_filelist] and old_entry[0] != "filelist.csv": 
            #filename not in new_filelist => deletion (skip filelist.csv)
            return_value["deleted_filelist"].append([old_entry[0],"delete",""])
    return return_value

def write_filelist_csv(folder, filelist):
    try:
        with open(folder+'/filelist.csv', 'w',newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            writer.writerows(filelist)
    except Exception as err:
        print("ERROR writing csv file in folder {}: {}".format(folder,err))
        sys.exit("Stopping execution")

def update_upd(folder):
    info = read_write_upd(folder = folder, info = upd_info(), read = True)
    now = datetime.now()
    new_compiled_date = int(now.strftime("%Y%m%d00"))
    if info.Device is not None:
        if new_compiled_date <= int(info.Compiled): # possible if multiple updates are published in one day (up to 99 updates possible)
            for i in range (100):
                new_compiled_date += 1
                if new_compiled_date > int(info.Compiled):
                    break
    else: #Device is None => there was no upd file so far => new module, create upd file
        info.Device = folder
    info.Compiled = str(new_compiled_date)
    read_write_upd(folder = folder, info = info, read = False) # update upd file

def read_write_upd(folder, info: upd_info, read: bool):
    path = folder + "\\" + folder + ".upd"
    if read:
        info = upd_info()
        try:
            with open(path, "r") as upd_file:
                for line in upd_file.readlines(): # walk through lines in upd file
                    for attrib in info.get_attributes():
                        if line.startswith(attrib):
                            setattr(info, attrib,line.split(': ')[1].splitlines()[0]) # remove linebreaks
            info.Device = folder # overwrite device name by folder name to make sure both match
            return info
        except FileNotFoundError:
            info.Device = None
            return info
        except Exception as err:
            print("ERROR reading .upd file in folder {}: {}".format(folder,err))
            sys.exit("Stopping execution")
    
    else: # write upd file
        try:
            with open(path, "w") as upd_file:
                for attrib in info.get_attributes():
                    upd_file.write(attrib + ': ' + getattr(info, attrib) + "\n")
        except Exception as err:
            print("ERROR writing .upd file in folder {}: {}".format(folder,err))
            sys.exit("Stopping execution")
        return

def write_Updates_csv():
    folders = os.listdir('.')
    folders.sort()
    update_array = []
    for folder in folders: # walk through all folders
        if os.path.isdir(folder): # take only fodlers into account
            info = read_write_upd(folder = folder, info = upd_info(), read = True)
            if info.Device is not None:
                update_array.append(info.Device + ';' + info.Compiled + ';')
            else:
                print("Upd file not found in folder {} to write into Updates.csv".format(folder))
                sys.exit("Stopping execution")
    try:
        with open("Updates.csv","w",encoding="utf-8") as updates_file:
            for entry in update_array:
                updates_file.write(entry)
                updates_file.write("\r")
    except Exception as err:
        print("ERROR writing Updates.csv in main folder: {}".format(err))
        sys.exit("Stopping execution")

def main():
    print("Python version: ")
    print(sys.version)
    if verbose: print("Loading online module list from thatec-innovation.com")
    online_modules = load_online_modules()
    all_module_folders = os.listdir('.')
    all_module_folders.sort()

    for folder in all_module_folders: # walk through all folders
        if os.path.isdir(folder):
            if folder in online_modules:
                print("ERROR: Folder name identical to existing device in THATec Innvovation online device library: {}".format(folder))
                print("Please read the readme file and rename the module folder accordingly!")
                sys.exit("Stopping execution")
            update = False
            if verbose: print("Current folder: {}".format(folder))
            new_filelist = get_files_in_folder(folder)
            if verbose: print("New filelist created")
            old_filelist = get_existing_filelist(folder)
            if old_filelist is not None:
                if verbose: print("Old filelist found, checking for new or deleted files")
                deletions = get_deleted_filelist_and_updates(old_filelist, new_filelist)
                if len(deletions["deleted_filelist"]) > 0 or deletions["update"]: # Deleted or updated files detected
                    print("Deleted or updated files detected in " + folder)
                    update = True
                    #print(new_filelist)
                    #print(deletions["deleted_filelist"])
                    new_filelist += deletions["deleted_filelist"] #removed items will be included into the filelist with a "delete" flag in column 1 and will be removed when updating via thaTEC:Core
                else:
                    if verbose: print("No deleted files found, checking upd file")
                    info = read_write_upd(folder = folder, info = upd_info(), read = True)
                    if info.Device is None: # upd does not exist
                        update = True
                        print("Upd file not found, creating new upd file")
            else: # no existing filelist found, check if upd file is available
                info = read_write_upd(folder = folder, info = upd_info(), read = True)
                if info.Device is None: # upd does not exist
                    update = True
                    print("New module found: {}".format(folder))
                else:
                    print("No filelist but upd file found in folder {}.")
                    x = input("Continue and create new filelist? (y/n):")
                    if x != 'y':
                        sys.exit('Stopping execution')
                    else:
                        update = True
            if update: # write filelist and upd file
                print("Updating upd file")
                update_upd(folder) # update upd file with new compiled date
                print("Updating filelist.csv")
                write_filelist_csv(folder, get_files_in_folder(folder)) #write new filelist to folder (update filelist since upd file has been updated)
    if verbose: print("=== Checking folders finished, writing Updates.csv")
    write_Updates_csv() # after writing all required files in module folders => write (global) Updates.csv containing the information on all modules

if __name__ == "__main__":
    main()