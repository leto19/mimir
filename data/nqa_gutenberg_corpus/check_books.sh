#!/bin/bash	

#finds books with less than 100 lines in the file (i.e. ones that probably didn't download properly)

for file in test/* train/* valid/*; 
	do myvar=($(less "$file" | wc));
		 if ((${myvar[0]} < 100)); 
			then echo $file; 
		fi; 
done
