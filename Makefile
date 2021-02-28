#NAME: Connor Daly, Ryan Daly
#EMAIL: connord2838@gmail.com, ryand3031@ucla.edu
#ID: 305416912, 505416119

build: lab3b.py
	rm -f lab3b
	ln -s lab3b.py lab3b
	chmod 777 lab3b
dist: build README
	tar -czvf lab3b-305416912.tar.gz lab3b.py README Makefile

clean:
	rm -f lab3b-305416912.tar.gz lab3b