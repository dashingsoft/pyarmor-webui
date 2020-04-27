*** Settings ***
Documentation     A single test to pack the obfuscated script to one folder.
...
...               Obfuscate main.py to pack all to one folder dist/main
...
Resource          resource.robot
Library           OperatingSystem
Test Teardown     Close Browser

*** Variables ***
${SRC}                 ${WORKPATH}/__src__
${FINAL BUNDLE}        ${SRC}/dist/main/main

*** Test Cases ***
Prepare Test Data
    Remove Directory    ${SRC}    True
    Create Directory    ${SRC}
    Create File    ${SRC}/main.py    print("This is pyarmor-webui test")

Pack Script To One Folder
    Open Browser To Home Page
    Click Home Tab Button    Pack Script Wizard
    Page Should Contain    Pack Script Wizard
    Input Src Path    ${SRC}
    Select Script    main.py
    Click Button    Pack
    Wait Until Building End
    Page Should Contain    Pack obfuscated scripts successfully

    Should Exist    ${FINAL BUNDLE}
    ${output}=    Run    ${FINAL BUNDLE}
    Should Contain    ${output}    This is pyarmor-webui test
