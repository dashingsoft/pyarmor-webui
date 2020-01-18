testcase=${1:-pyarmor_webui_suite.robot}

workpath=__runner__

rm -rf $workpath
mkdir -p $workpath

cd $workpath
robot ../$testcase
