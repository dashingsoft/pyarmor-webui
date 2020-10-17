*** Settings ***
Documentation     A single test to obfuscated multiple entries.
...
...               Obfuscate main.py and foo.py as entry script
...
Resource          resource.robot
Library           OperatingSystem
Test Teardown     Close Browser

*** Variables ***
${SRC}                 ${WORKPATH}/__src__
${DIST}                ${SRC}/dist

*** Test Cases ***
Prepare Test Data
    Remove Directory    ${SRC}    True
    Create Directory    ${SRC}
    Create File    ${SRC}/main.py    print("This is main")
    Create File    ${SRC}/foo.py    print("This is foo")

Obfuscate Multiple Entries
    Open Browser To Home Page
    Click Home Tab Button    Obfuscate Script Wizard

    Page Should Contain    Obfuscate Script Wizard
    Input Src Path    ${SRC}
    Select Include Mode    Only the scripts list above
    Select Two Scripts    main.py    foo.py
    Click Button    Obfuscate
    Wait Until Building End
    Page Should Contain    Obfuscate the scripts successfully

    Should Exist    ${DIST}/main.py
    Should Exist    ${DIST}/foo.py
    ${output}=    Run    python ${DIST}/main.py
    Should Contain    ${output}    This is main
    ${output}=    Run    python ${DIST}/foo.py
    Should Contain    ${output}    This is foo
