*** Settings ***
Documentation     A resource file with reusable keywords and variables.
...
...               The system specific keywords created here form our own
...               domain specific language. They utilize keywords provided
...               by the imported SeleniumLibrary.
Library           SeleniumLibrary

*** Variables ***
${SERVER}         http://localhost:8080
${BROWSER}        Firefox
${DELAY}          0

*** Keywords ***
Open Browser To Home Page
    Open Browser    ${SERVER}    ${BROWSER}
    Maximize Browser Window
    Set Selenium Speed    ${DELAY}
    Home Page Should Be Open

Home Page Should Be Open
    Title Should Be    PyArmor

Click Home Tab Button
    [Arguments]    ${title}
    Click Button    ${title}

Click Aside Menu
    [Arguments]    ${title}
    Click Element    //li[@class="el-menu-item" and child::span = "${title}"]

Input Form Field
    [Arguments]    ${label}    ${value}
    Input Text    //div[@class="el-form-item" and descendant::label = "${label}"]/descendant::input[@class="el-input__inner"]    ${value}

Input Expired Date
    [Arguments]    ${date}
    Input Text    name:expired    ${date}

Message Should Be Shown
    [Arguments]    ${text}
    Page Should Contain    ${text}
