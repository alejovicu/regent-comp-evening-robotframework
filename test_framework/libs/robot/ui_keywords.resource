*** Settings ***
Documentation     Generic UI keywords on top of SeleniumLibrary, not tied to any page.
Variables         ../../config/config.py
Library           SeleniumLibrary    timeout=${TIMEOUT}    run_on_failure=Capture Page Screenshot


*** Variables ***
${PAGE_TITLE}      id:page-title
${FLASH_MESSAGE}   id:flash-message
${FLASH_TEXT}      id:flash-text


*** Keywords ***
Wait Until Element Text Is
    [Arguments]    ${locator}    ${expected}
    Wait Until Keyword Succeeds    ${TIMEOUT}    200ms
    ...    Element Text Should Be    ${locator}    ${expected}

Wait Until Element Count Is
    [Arguments]    ${locator}    ${expected}
    Wait Until Keyword Succeeds    ${TIMEOUT}    200ms
    ...    Page Should Contain Element    ${locator}    limit=${expected}

Wait Until Attribute Is
    [Arguments]    ${locator}    ${attribute}    ${expected}
    Wait Until Keyword Succeeds    ${TIMEOUT}    200ms
    ...    Element Attribute Value Should Be    ${locator}    ${attribute}    ${expected}

Flash Message Should Be
    [Documentation]    Checks the single feedback area every page has.
    ...    ``type`` is ``success``, ``warning`` or ``error``.
    [Arguments]    ${type}    ${text}
    Wait Until Element Is Visible    ${FLASH_MESSAGE}
    Wait Until Element Text Is    ${FLASH_TEXT}    ${text}
    Wait Until Attribute Is    ${FLASH_MESSAGE}    data-type    ${type}

Fill Field
    [Documentation]    Replaces the field's value by typing; an empty ``value`` empties it.
    [Arguments]    ${locator}    ${value}
    IF    $value
        Input Text    ${locator}    ${value}    clear=True
    ELSE
        Set Input Value    ${locator}    ${EMPTY}
    END

Set Input Value
    [Documentation]    Sets the whole value in one input event, like pasting.
    ...    Selenium's clear() does not trigger React's onChange, and typing
    ...    fires one event per character; this does neither.
    [Arguments]    ${locator}    ${value}
    ${element}=    Get WebElement    ${locator}
    Execute Javascript
    ...    const [el, value] = arguments;
    ...    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
    ...    setter.call(el, value);
    ...    el.dispatchEvent(new Event('input', { bubbles: true }));
    ...    ARGUMENTS    ${element}    ${value}
