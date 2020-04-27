# Run one or more test cases
#
# 1. Run all the test cases list in this directory:
#
#     bash run-test.sh
#
# 2. Run one test case
#
#    bash run-test.sh generate_expired_license.robot
#
workpath=__runner__

rm -rf $workpath
mkdir -p $workpath

cd $workpath
robot ../$testcase
