count=2
./lab3b testEXT2.csv 1>/dev/null
if [ $? -ne 0 ]
then
    echo "failed to exit with code 0"
    count=$((count-1))
fi 

./lab3b test.csv 1>/dev/null
if [ $? -ne 2 ]
then
    echo "failed to exit with code 0"
    count=$((count-1))
fi 

echo "passed $count / 2 test cases"