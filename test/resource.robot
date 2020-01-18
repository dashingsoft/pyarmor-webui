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
${DATAHOME}       /Users/jondy/.pyarmor
${WORKPATH}       /Users/jondy/workspace/pyarmor-webui/test/__runner__

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
    ${elem} =    Get WebElement    //div[@class="el-form-item" and descendant::label = "${label}"]/descendant::input[@class="el-input__inner"]
    Input Text    ${elem}    ${value}

Input Select Field
    [Arguments]    ${label}    ${value}
    ${elem} =    Get WebElement    //div[@class="el-form-item" and descendant::label = "${label}"]/descendant::input[@class="el-select__input"]
    Click Element    ${elem}
    Press Keys    None    ${value}    RETURN
    Sleep    1s
    Press Keys    None    TAB

Input Textarea Field
    [Arguments]    ${label}    ${value}
    Input Text    //div[@class="el-form-item" and descendant::label = "${label}"]/descendant::textarea[@class="el-textarea__inner"]    ${value}

Input Src Path
    [Arguments]    ${value}
    ${elem} =    Get WebElement    //div[@class="el-form-item is-required" and descendant::label = "Src"]/descendant::input[@class="el-input__inner"]
    Click Element    ${elem}
    Input Text    ${elem}    ${value}
    Simulate Event    ${elem}    blur
    Sleep    1s
    Press Keys    None    TAB
    Wait Until Element Is Not Visible    //div[@class="el-select-dropdown el-popper"]
    Sleep    1s

Select Script
    [Arguments]    ${value}
    ${elem} =    Get WebElement    //div[@class="el-form-item is-required" and descendant::label = "Script"]/descendant::input[@class="el-input__inner"]
    Click Element    ${elem}
    Wait Until Element Is Visible    //ul[@class="el-scrollbar__view el-cascader-menu__list"]
    Click Element    //ul[@class="el-scrollbar__view el-cascader-menu__list"]/li[span = "${value}"]
    Wait Until Element Is Not Visible    //ul[@class="el-scrollbar__view el-cascader-menu__list"]

Select Bundle
    [Arguments]    ${value}
    ${elem} =    Get WebElement    //div[@class="el-form-item" and descendant::label = "Bundle"]/descendant::input[@class="el-input__inner"]
    Click Element    ${elem}
    Sleep    1s
    Click Element    //ul[@class="el-scrollbar__view el-select-dropdown__list"]/li[span = "${value}"]
    Wait Until Element Is Not Visible    //div[@class = "el-select-dropdown el-popper"]

Input Bundle Name
    [Arguments]    ${value}
    ${elem} =    Get WebElement    //div[@class="el-form-item" and descendant::label = "Bundle"]/descendant::input[@class="el-input__inner"][2]
    Click Element    ${elem}
    Input Text    ${elem}    ${value}

Input Path Field
    [Arguments]    ${label}    ${value}
    ${elem} =    Get WebElement    //div[@class="el-form-item" and descendant::label = "${label}"]/descendant::input[@class="el-input__inner"]
    Click Element    ${elem}
    Input Text    ${elem}    ${value}
    Simulate Event    ${elem}    blur
    Set Browser Implicit Wait    2s

Input File Field
    [Arguments]    ${label}    ${value}
    ${elem} =    Get WebElement    //div[@class="el-form-item" and descendant::label = "${label}"]/descendant::input[@class="el-input__inner"]
    Input Text    ${locator}    ${value}
    Press Keys    RETURN

Wait Until Building End
    Wait Until Page Contains Element    //div[@class="el-message el-message--info"]/p[@class="el-message__content"]    30 seconds

Input Expired Date
    [Arguments]    ${date}
    Input Text    name:expired    ${date}

Message Should Be Shown
    [Arguments]    ${text}
    Page Should Contain    ${text}
