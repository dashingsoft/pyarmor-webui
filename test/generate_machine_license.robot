*** Settings ***
Documentation     A single test to generate license for fixed machine.
...
...               This test has a workflow that is created using keywords in
...               the imported resource file.
Resource          resource.robot

*** Variables ***
${HARDDISK}                 FV994730S6LLF07AY
${MAC}                      f8:ff:c2:27:00:7f
${IPV4}                     192.168.121.102

*** Test Cases ***
Generate Expired License
    Open Browser To Home Page
    Click Home Tab Button    Fixed Machine License
    Page Should Contain    New License
    Input Form Field    Harddisk    ${HARDDISK}
    Input Form Field    IPv4    ${IPV4}
    Input Form Field    Mac    ${MAC}
    Click Button    Create
    Message Should Be Shown    The license has been saved to

    Click Aside Menu    My Licenses
    Page Should Contain    ${HARDDISK}
    [Teardown]    Close Browser
