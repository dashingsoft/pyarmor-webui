*** Settings ***
Documentation     A single test to generate license with extra data.
...
...               This test has a workflow that is created using keywords in
...               the imported resource file.
Resource          resource.robot
Library           OperatingSystem

*** Variables ***
${EXTRADATA}                 Pro-Version Expired on 2020-05-20

*** Test Cases ***
Generate Expired License
    Open Browser To Home Page
    Click Home Tab Button    Full Features License
    Page Should Contain    New License
    Input Textarea Field    Extra Data    ${EXTRADATA}
    Click Button    Create
    Message Should Be Shown    The license has been saved to

    Click Aside Menu    My Licenses
    Page Should Contain    Extra data
    [Teardown]    Close Browser
