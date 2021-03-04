#!/usr/bin/python

import csv, sys

Inodes = []
Bfrees = set([])
Ifrees = set([])
Dirents = []
Indirects = []
Groups = []
#occupiedBlocks = set([])
#tracks all the blocks that are referenced
referencedBlocks = dict([])
#counts how many directories an inode says its referenced by
linkCounts = dict([])
#counts how many directories are referenced by an inode
linksFound = dict([])
#for each child directory stores their parent
childParentDirs = dict([])

def main():
   inconsistencyFound = False
   if len(sys.argv) != 2:
      sys.stderr.write("please use one and only one argument")
      exit(1)
   #to check if file is valid
   try:
      csvFile = open(sys.argv[1])
   except:
      sys.stderr.write("Error: couldn't open specified file")
      exit(1)
   
   #Go through the file and sort the different lines into lists
   #Also should do anything with the Superblock here
   #Also maybe the Group stuff since I think there might only be one group always, but it probably wouldn't be hard to assume multiple groups
   with open(sys.argv[1]) as csvFile:
      reader = csv.reader(csvFile)
      for line in reader:
         identifier = line[0]
         if (identifier == 'SUPERBLOCK'):
            numInodes = int(line[2])
            firstNonReservedInode = int(line[7])
            maxBlockNum = int(line[1])
            blockSize = int(line[3])
            inodeSize = int(line[4])
         elif identifier == 'GROUP':
            #Groups.append(line)
            Bbitmap = int(line[6])
            Ibitmap = int(line[7])
            reserved = int(line[8]) + inodeSize*int(line[3])/blockSize
         elif identifier == 'BFREE':
            Bfrees.add(int(line[1]))
         elif identifier == 'IFREE':
            Ifrees.add(int(line[1])) 
         elif identifier == 'DIRENT':
            Dirents.append(line)
         elif identifier == 'INODE':
            Inodes.append(line)
         elif identifier == 'INDIRECT':
            Indirects.append(line)
            if line[5] in referencedBlocks:
               referencedBlocks[int(line[5])] += 1
            else:
               referencedBlocks[int(line[5])] = 1
            
  
   #indirects check
   for line in Indirects:
      blockNum = int(line[5])
      #print(blockNum)
      level = int(line[2])
      #check for invalid          
      if blockNum < 0 or blockNum > maxBlockNum:
         print("test")
         if level == 1:
            print("INVALID INDIRECT BLOCK " + str(blockNum) + " IN INODE " + line[1] + " AT OFFSET 12")
            inconsistencyFound = True
         elif level == 2:
            print("INVALID DOUBLE INDIRECT BLOCK " + str(blockNum) + " IN INODE " + line[1] + " AT OFFSET 268")
            inconsistencyFound = True
         elif level == 3:
            print("INVALID TRIPLE INDIRECT BLOCK " + str(blockNum) + " IN INODE " + line[1] + " AT OFFSET 65804") 
            inconsistencyFound = True
         #Check for reserved
      if blockNum != 0 and blockNum < reserved:
         if level == 1:
            print("RESERVED INDIRECT BLOCK " + str(blockNum) + " IN INODE " + line[1] + " AT OFFSET 12")
            inconsistencyFound = True
         elif level == 2:
            print("RESERVED DOUBLE INDIRECT BLOCK " + str(blockNum) + " IN INODE " + line[1] + " AT OFFSET 268")
            inconsistencyFound = True
         elif level == 3:
            print("RESERVED TRIPLE INDIRECT BLOCK " + str(blockNum) + " IN INODE " + line[1] + " AT OFFSET 65804")  
            inconsistencyFound = True

   #Inode part
   for line in Inodes:
      #might have to check if the mode is 0 of the inodes
      if int(line[1]) in Ifrees:
         print("ALLOCATED INODE " + line[1] + " ON FREELIST")
         inconsistencyFound = True
         Ifrees.remove(int(line[1]))
      #Ifrees.add(int(line[1]))
      linkCounts.update({int(line[1]): int(line[6])}) 
      if line[2] != "s" or int(line[10]) >= 60:
         for i in range(0, 15):
            blockNum = int(line[12+i])
            #occupiedBlocks.add(blockNum)
            #used to check for duplicates or unreferenced blocks
            if blockNum in referencedBlocks:
               referencedBlocks[blockNum] += 1
            else:
               referencedBlocks[blockNum] = 1
            #check for invalid          
            if blockNum < 0 or blockNum > maxBlockNum:
               if i < 12:
                  print("INVALID BLOCK " + str(blockNum) + " IN INODE " + line[1] + " AT OFFSET " + str(i))
                  inconsistencyFound = True
               elif i == 12:
                  print("INVALID INDIRECT BLOCK " + str(blockNum) + " IN INODE " + line[1] + " AT OFFSET 12")
                  inconsistencyFound = True
               elif i == 13:
                  print("INVALID DOUBLE INDIRECT BLOCK " + str(blockNum) + " IN INODE " + line[1] + " AT OFFSET 268")
                  inconsistencyFound = True
               elif i == 14:
                  print("INVALID TRIPLE INDIRECT BLOCK " + str(blockNum) + " IN INODE " + line[1] + " AT OFFSET 65804") 
                  inconsistencyFound = True
            #Check for reserved
            if blockNum != 0 and blockNum < reserved:
               if i < 12:
                  print("RESERVED BLOCK " + str(blockNum) + " IN INODE " + line[1] + " AT OFFSET " + str(i))
                  inconsistencyFound = True
               elif i == 12:
                  print("RESERVED INDIRECT BLOCK " + str(blockNum) + " IN INODE " + line[1] + " AT OFFSET 12")
                  inconsistencyFound = True
               elif i == 13:
                  print("RESERVED DOUBLE INDIRECT BLOCK " + str(blockNum) + " IN INODE " + line[1] + " AT OFFSET 268")
                  inconsistencyFound = True
               elif i == 14:
                  print("RESERVED TRIPLE INDIRECT BLOCK " + str(blockNum) + " IN INODE " + line[1] + " AT OFFSET 65804")    
                  inconsistencyFound = True                
   
   #check for allocated blocks in freelist
   for i in Bfrees:
      if i in referencedBlocks:
         print("ALLOCATED BLOCK " + str(i) + " ON FREELIST")
         inconsistencyFound = True
      else: 
         #print(i)
         referencedBlocks[i] = 1
         #print(i in referencedBlocks)
      
   #check unreferenced blocks
   for i in range(reserved +1, maxBlockNum):
      if not int(i) in referencedBlocks:
         r = 0
         print("UNREFERENCED BLOCK " + str(i))
         inconsistencyFound = True
         #print(referencedBlocks[i])

   #directory part
   for line in Dirents:
      inodeNum = int(line[3])
      if inodeNum in linksFound:
         linksFound[inodeNum] += 1
      else:
         linksFound.update({inodeNum : 1})
      if inodeNum < 1 or inodeNum > numInodes:
         print("DIRECTORY INODE " + line[1] + " NAME " + line[6] + " INVALID INODE " + str(inodeNum))
         inconsistencyFound = True
      #might have to check the inodes and if it has mode == 0
      elif inodeNum in Ifrees:
         print("DIRECTORY INODE " + line[1] + " NAME " + line[6] + " UNALLOCATED INODE " + str(inodeNum))
         inconsistencyFound = True
      elif line[6] == "'.'" and int(line[1]) != inodeNum:
         print("DIRECTORY INODE " + line[1] + " NAME " + line[6] + " LINK TO INODE " + str(inodeNum) + " SHOULD BE " + line[1])
         inconsistencyFound = True
      elif line[6] != "'.'" and line[6] != "'..'" :
         #print(str(inodeNum) + " " + line[1])
         childParentDirs.update({int(inodeNum) : int(line[1])})
      #need to have the checking for parent directory part
      #elif line[6] == "'..'" and int(line[1]) != inodeNum:
         #print("DIRECTORY INODE " + line[1] + " NAME " + line[6] + " LINK TO INODE " + str(inodeNum) + " SHOULD BE " + line[1])

   #check for .. links correct
   for line in Dirents:
      if line[6] == "'..'":
         #print(line)
         #idk what to do if its not, i dont think that could happen - for some reason sometimes 2 is the parent even though idk why so I'm assuming if parent isn't given that it's 2
         if int(line[1]) in childParentDirs:
            #print(str(childParentDirs[int(line[1])]) + " " + line[3])
            if childParentDirs[int(line[1])] != int(line[3]):
               print("DIRECTORY INODE " + line[1] + " NAME " + line[6] + " LINK TO INODE " + line[3] + " SHOULD BE " + str(childParentDirs[int(line[1])]))
               inconsistencyFound = True
         elif int(line[3]) != 2:
            print("DIRECTORY INODE " + line[1] + " NAME " + line[6] + " LINK TO INODE " + line[3] + " SHOULD BE 2")
            inconsistencyFound = True

   #check for numLinks
   for node in linkCounts:
      if not node in linksFound:
         print("INODE " + str(node) + " HAS 0 LINKS BUT LINKCOUNT IS " + str(linkCounts[node]))
         inconsistencyFound = True
      elif linkCounts[node] != linksFound[node]:
         print("INODE " + str(node) + " HAS " + str(linksFound[node]) + " LINKS BUT LINKCOUNT IS " + str(linkCounts[node]))
         inconsistencyFound = True
   #check duplicates
   for line in Inodes:
      #for checking unallocated node not in list
      #print(line)
      Ifrees.add(int(line[1]))
      if line[2] != 's' or int(line[10]) >= 60:
         for i in range(0, 15):
            blockNum = int(line[12+i])
            if blockNum != 0 and blockNum in referencedBlocks:
               if referencedBlocks[blockNum] > 1:
                  if i < 12:
                     print("DUPLICATE BLOCK " + str(blockNum) + " IN INODE " + line[1] + " AT OFFSET " + str(i))
                     inconsistencyFound = True
                  elif i == 12:
                     print("DUPLICATE INDIRECT BLOCK " + str(blockNum) + " IN INODE " + line[1] + " AT OFFSET 12")
                     inconsistencyFound = True
                  elif i == 13:
                     print("DUPLICATE DOUBLE INDIRECT BLOCK " + str(blockNum) + " IN INODE " + line[1] + " AT OFFSET 268")
                     inconsistencyFound = True
                  elif i == 14:
                     print("DUPLICATE TRIPLE INDIRECT BLOCK " + str(blockNum) + " IN INODE " + line[1] + " AT OFFSET 65804")
                     inconsistencyFound = True

   #check for unallocated Inodes
   for i in range(firstNonReservedInode, numInodes+1):
      if not i in Ifrees:
         print("UNALLOCATED INODE " + str(i) + " NOT ON FREELIST")
         inconsistencyFound = True
   
   if inconsistencyFound:
      exit(2)
   exit(0)

if __name__ == "__main__":
    main()