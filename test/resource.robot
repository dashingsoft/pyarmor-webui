*** Settings ***
Documentation     A resource file with reusable keywords and variables.
...
...               The system specific keywords created here form our own
...               domain specific language. They utilize keywords provided
...               by the imported SeleniumLibrary.
Library           SeleniumLibrary

*** Variables ***
${SERVER}         http://localhost:9096
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

Input Path
    [Arguments]    ${label}    ${value}
    ${elem} =    Get WebElement    //div[starts-with(@class, "el-form-item") and descendant::label = "${label}"]/descendant::input[@class="el-input__inner"]
    Click Element    ${elem}
    Input Text    ${elem}    ${value}
    Simulate Event    ${elem}    blur
    Sleep    1s
    Press Keys    None    TAB
    Wait Until Element Is Not Visible    //div[@class="el-select-dropdown el-popper"]
    Sleep    1s

Input Src Path
    [Arguments]    ${value}
    Input Path    Src    ${value}

Input Output Path
    [Arguments]    ${value}
    Input Path    Output    ${value}

Select Script
    [Arguments]    ${value}
    ${elem} =    Get WebElement    //div[@class="el-form-item is-required" and descendant::label = "Script"]/descendant::input[@class="el-input__inner"]
    Click Element    ${elem}
    Wait Until Element Is Visible    //ul[@class="el-scrollbar__view el-cascader-menu__list"]
    Click Element    //ul[@class="el-scrollbar__view el-cascader-menu__list"]/li[span = "${value}"]
    Wait Until Element Is Not Visible    //ul[@class="el-scrollbar__view el-cascader-menu__list"]

Select One Script
    [Arguments]    ${value}
    ${elem} =    Get WebElement    //div[@class="el-form-item" and descendant::label = "Script"]/descendant::input[@class="el-input__inner"]
    Click Element    ${elem}
    Wait Until Element Is Visible    //div[@class="el-popper el-cascader__dropdown" and not(contains(@style, "display: none"))]
    Click Element    //div[@class="el-popper el-cascader__dropdown" and not(contains(@style, "display: none"))]//ul[@class="el-scrollbar__view el-cascader-menu__list"]/li[span = "${value}"]
    Wait Until Element Is Not Visible    //ul[@class="el-scrollbar__view el-cascader-menu__list"]

Select Two Scripts
    [Arguments]    ${one}    ${two}
    ${dropdown menu} =    Set Variable    //div[@class="el-popper el-cascader__dropdown" and not(contains(@style, "display: none"))]
    Click Element    //div[@class="el-form-item" and descendant::label = "Scripts"]/descendant::input[@class="el-cascader__search-input"]
    Wait Until Element Is Visible    ${dropdown menu}
    Click Element    ${dropdown menu}//li[@class="el-cascader-node" and span="${one}"]//span[@class="el-checkbox__input"]
    Click Element    ${dropdown menu}//li[@class="el-cascader-node" and span="${two}"]//span[@class="el-checkbox__input"]
    Wait Until Element Is Not Visible    //ul[@class="el-scrollbar__view el-cascader-menu__list"]

Select Include Mode
    [Arguments]    ${value}
    ${elem} =    Get WebElement    //div[@class="el-form-item" and descendant::label = "Include"]/descendant::input[@class="el-input__inner"]
    Click Element    ${elem}
    Sleep    1s
    Click Element    //ul[@class="el-scrollbar__view el-select-dropdown__list"]/li[span = "${value}"]
    Sleep    1s

Switch Package Name
    Click Element    //div[@class="el-form-item" and descendant::label = "Package Name"]/descendant::div[@class="el-switch"]

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
    Click Element    //label["Expired"]
    Sleep    1s

Message Should Be Shown
    [Arguments]    ${text}
    Page Should Contain    ${text}
