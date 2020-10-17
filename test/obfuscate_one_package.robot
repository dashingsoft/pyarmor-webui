*** Settings ***
Documentation     A single test to obfuscated one package.
...
...               Obfuscate package "cook"
...
Resource          resource.robot
Library           OperatingSystem
Test Teardown     Close Browser

*** Variables ***
${SRC}                 ${WORKPATH}/__src__
${DIST}                ${SRC}/cook/dist

*** Test Cases ***
Prepare Test Data
    Remove Directory    ${SRC}    True
    Create Directory    ${SRC}
    Create Directory    ${SRC}/cook
    Create File    ${SRC}/cook/__init__.py    print("This is pyarmor-webui test")
    Create File    ${SRC}/main.py    import cook
    

Obfuscate One Package
    Open Browser To Home Page
    Click Home Tab Button    Obfuscate Script Wizard

    Page Should Contain    Obfuscate Script Wizard
    Input Src Path    ${SRC}/cook
    Select One Script    __init__.py
    Click Button    Next
    Click Button    Next
    Switch Package Name
    Click Button    Obfuscate
    Wait Until Building End
    Page Should Contain    Obfuscate the scripts successfully

    Should Exist    ${DIST}/cook/__init__.py
    Copy File    ${SRC}/main.py    ${DIST}
    ${output}=    Run    python ${DIST}/main.py
    Should Contain    ${output}    This is pyarmor-webui test
