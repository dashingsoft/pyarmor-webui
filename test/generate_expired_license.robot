*** Settings ***
Documentation     A single test to generate expired license.
...
...               This test has a workflow that is created using keywords in
...               the imported resource file.
Resource          resource.robot

*** Variables ***
${EXPIRED}               2021-10-15

*** Test Cases ***
Generate Expired License
    Open Browser To Home Page
    Click Home Tab Button    Generate Expired License
    Page Should Contain    New License
    Input Expired Date    ${EXPIRED}
    Click Button    Create
    Message Should Be Shown    The license has been saved to

    Click Aside Menu    My Licenses
    Page Should Contain    ${EXPIRED}
    [Teardown]    Close Browser
