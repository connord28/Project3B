#!/usr/bin/python

import csv, sys

Inodes = []
Bfrees = set([])
Ifrees = set([])
Dirents = []
Indirects = []
Groups = []
occupiedBlocks = set([])
referencedBlocks = dict([])

def main():
   if len(sys.argv) != 2:
      sys.stderr.write("please use one and only one argument\n")
      exit(1)
   #to check if file is valid
   try:
      csvFile = open(sys.argv[1])
   except:
      sys.stderr.write("Error: couldn't open specified file\n")
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
            Bfrees.add(line[1])
         elif identifier == 'IFREE':
            Ifrees.add(line[1]) 
         elif identifier == 'DIRENT':
            Dirents.append(line)
         elif identifier == 'INODE':
            Inodes.append(line)
         elif identifier == 'INDIRECT':
            Indirects.append(line)
  
   #Inode part
   for line in Inodes:
      if line[1] in Ifrees:
         print("Allocated INODE " + line[1] + " ON FREELIST\n")
      Ifrees.add(line[1])
      if line[2] != "s":
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
               elif i == 12:
                  print("INVALID INDIRECT BLOCK " + str(blockNum) + " IN INODE " + line[1] + " AT OFFSET 12")
               elif i == 13:
                  print("INVALID DOUBLE INDIRECT BLOCK " + str(blockNum) + " IN INODE " + line[1] + " AT OFFSET 268")
               elif i == 14:
                  print("INVALID TRIPLE INDIRECT BLOCK " + str(blockNum) + " IN INODE " + line[1] + " AT OFFSET 65804") 
            #Check for reserved
            if blockNum != 0 and blockNum < reserved:
               if i < 12:
                  print("RESERVED BLOCK " + str(blockNum) + " IN INODE " + line[1] + " AT OFFSET " + str(i))
               elif i == 12:
                  print("RESERVED INDIRECT BLOCK " + str(blockNum) + " IN INODE " + line[1] + " AT OFFSET 12")
               elif i == 13:
                  print("RESERVED DOUBLE INDIRECT BLOCK " + str(blockNum) + " IN INODE " + line[1] + " AT OFFSET 268")
               elif i == 14:
                  print("RESERVED TRIPLE INDIRECT BLOCK " + str(blockNum) + " IN INODE " + line[1] + " AT OFFSET 65804")                       
   
   #check for unallocated Inodes
   for i in range(firstNonReservedInode, numInodes+1):
      if not str(i) in Ifrees:
         print("UNALLOCATED INODE " + str(i) + " NOT ON FREELIST")

   #check for duplicate references to blocks or unreferenced blocks

   #directory part        

if __name__ == "__main__":
    main()