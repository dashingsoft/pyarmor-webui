*** Settings ***
Documentation     A single test to pack the obfuscated script to one file.
...
...               Obfuscate main.py to pack all to one file "dist/myapp" but
...               without license.
...
Resource          resource.robot
Library           OperatingSystem
Test Teardown     Close Browser

*** Variables ***
${SRC}                 ${WORKPATH}/__src__
${FINAL BUNDLE}        ${SRC}/dist/myapp
${OUTER LICENSE}       ${DATAHOME}/licenses/reg-000001/license.lic

*** Test Cases ***
Prepare Test Data
    Remove Directory    ${SRC}    True
    Create Directory    ${SRC}
    Create File    ${SRC}/main.py    print("This is pyarmor-webui test")
    Should Exist    ${OUTER LICENSE}

Pack One File Bundle With Outer License
    Open Browser To Home Page
    Click Home Tab Button    Pack Script Wizard
    Page Should Contain    Pack Script Wizard
    Input Src Path    ${SRC}
    Select Script    main.py
    Click Button    Next
    Click Button    Next
    Click Button    Next
    Select Bundle    all to one file with outer license
    Input Bundle Name    myapp
    Click Button    Pack
    Wait Until Building End
    Page Should Contain    Pack obfuscated scripts successfully

    Should Exist    ${FINAL BUNDLE}
    ${rc} =    Run and Return RC    ${FINAL BUNDLE}
    Should Be True    ${rc} > 0

    Copy File    ${OUTER LICENSE}    ${SRC}/dist
    ${output}=    Run    ${FINAL BUNDLE}
    Should Contain    ${output}    This is pyarmor-webui test
