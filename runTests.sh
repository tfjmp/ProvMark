#!/bin/bash

if [[ "$#" -ne 3 || ("$3" != "rb" && "$3" != "rg" && "$3" != "rh") ]] 
then
	echo "Usage: "$0" <Tools> <Tools_Path> <Result Type>"
	echo "Result Type:"
	echo "rb: benchmark only"
	echo "rg: benchmark and generalized foreground and background graph only"
	echo "rh: html page displaying benchmark and generalied foreground and background graph"
	exit 1
fi

sudo mkdir finalResult > /dev/null 2>&1
row=""
for i in `ls benchmarkProgram/baseSyscall`
do
	for j in `ls benchmarkProgram/baseSyscall/$i`
	do
		syscall=${j:3}
		syscall=${syscall,,}
		if [ -e finalResult/$syscall ]
		then
			sudo rm -f finalResult/$syscall/*
		else		
			sudo mkdir finalResult/$syscall > /dev/null 2>&1
		fi

		echo "Generating provenance benchmark for $syscall in group $i using $1 settings..."
		sudo ./fullAutomation.py $1 $2 benchmarkProgram/baseSyscall/$i/$j 
		
####################################################Temporary fix for displaying 1 benchmark result only#################################

		for result in `ls result/result-*.clingo`
		do
			sudo genClingoGraph/clingo2Dot.py result/$result result.dot
			sudo dot -Tsvg -o "finalResult/$syscall/benchmark.svg" result.dot
			sudo rm -f result.dot
		done

		if [ "$3" != "rb" ]
		then
			for result in `ls result/general.clingo-control*`
			do
				sudo genClingoGraph/clingo2Dot.py result/$result control.dot
				sudo dot -Tsvg -o "finalResult/$syscall/background.svg" control.dot
				sudo rm -f control.dot
			done

			for result in `ls result/general.clingo-program*`
			do
				sudo genClingoGraph/clingo2Dot.py result/$result program.dot
				sudo dot -Tsvg -o "finalResult/$syscall/foreground.svg" program.dot
				sudo rm -f program.dot
			done

			if [ "$3" = "rh" ]
			then
				row=$row$(cat template/row.html | sed "s|@@@SYSCALL@@@|${syscall}|g")
			fi
		fi

##################################################End of Temporary Fix###################################################################


		echo "Process complete for $syscall."
	done
done

if [ "$3" = "rh" ]
then
	html=$(sudo cat template/base.html)
        echo "${html%@@@TABLEROW@@@*} $row ${html##*@@@TABLEROW@@@}" | sudo tee finalResult/index.html > /dev/null
fi

echo "Process done. Result in finalResult directory."
