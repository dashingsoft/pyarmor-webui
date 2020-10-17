*** Settings ***
Documentation     A single test to obfuscated one script.
...
...               Obfuscate main.py and all the other `.py` files
...
Resource          resource.robot
Library           OperatingSystem
Test Teardown     Close Browser

*** Variables ***
${SRC}                 ${WORKPATH}/__src__
${OUTPUT}              ${SRC}/dist

*** Test Cases ***
Prepare Test Data
    Remove Directory    ${SRC}    True
    Create Directory    ${SRC}
    Create File    ${SRC}/cook.py    print("This is pyarmor-webui test")
    Create File    ${SRC}/main.py    __import__("cook")
    Create File    ${SRC}/README    This is data file

Obfuscate One Script
    Open Browser To Home Page
    Click Home Tab Button    Obfuscate Script Wizard

    Page Should Contain    Obfuscate Script Wizard
    Input Src Path    ${SRC}
    Select One Script    main.py
    Click Button    Obfuscate
    Wait Until Building End
    Page Should Contain    Obfuscate the scripts successfully

    Should Exist    ${OUTPUT}/main.py
    Should Exist    ${OUTPUT}/cook.py
    ${output}=    Run    python ${OUTPUT}/main.py
    Should Contain    ${output}    This is pyarmor-webui test
