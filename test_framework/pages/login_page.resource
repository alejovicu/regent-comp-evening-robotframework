*** Settings ***
Documentation     Page object: /login
Resource          ../resources/common.resource


*** Variables ***
${LOGIN_URL}             ${BASE_URL}/login
${LOGIN_USERNAME}        id:username
${LOGIN_PASSWORD}        id:password
${LOGIN_BUTTON}          id:login-button
${HEADER_USER}           id:current-user


*** Keywords ***
Open Login Page Logged Out
    [Documentation]    Drops any stored session so the login form is shown.
    Go To    ${LOGIN_URL}
    Execute Javascript    window.localStorage.clear()
    Reload Page
    Wait Until Element Is Visible    ${LOGIN_USERNAME}

Log In
    [Arguments]    ${username}    ${password}
    Open Login Page Logged Out
    Input Text    ${LOGIN_USERNAME}    ${username}
    Input Password    ${LOGIN_PASSWORD}    ${password}
    Click Button    ${LOGIN_BUTTON}
    Wait Until Element Text Is    ${HEADER_USER}    ${username}
