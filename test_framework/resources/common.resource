*** Settings ***
Documentation     Shared imports and session keywords for every suite.
Variables         ../config/config.py
Library           ../libs/python/CatalogApi.py    ${BASE_URL}
Resource          ../libs/robot/ui_keywords.resource


*** Keywords ***
Start Test Session
    Open Browser    ${BASE_URL}    ${BROWSER}    remote_url=${REMOTE_URL}
    Set Window Size    ${WINDOW_WIDTH}    ${WINDOW_HEIGHT}

End Test Session
    Close All Browsers

Restore Demo Data
    [Documentation]    Puts the backend back to the 6 sample products, through the API.
    Authenticate As    ${ADMIN}[username]    ${ADMIN}[password]
    Reset Demo Data
