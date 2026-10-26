*** Settings ***
Library           SeleniumLibrary

*** Test Cases ***
Check Regent Site is OK
    Open Browser    https://www.regent.se     Chrome
    Sleep  5


