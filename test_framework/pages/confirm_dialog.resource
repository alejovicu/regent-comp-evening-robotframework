*** Settings ***
Documentation     Page object: in-page confirmation dialog (used before deleting)
Resource          ../resources/common.resource


*** Variables ***
${CONFIRM_DIALOG}      id:confirm-dialog
${CONFIRM_MESSAGE}     id:confirm-message
${CONFIRM_YES}         id:confirm-yes
${CONFIRM_NO}          id:confirm-no


*** Keywords ***
Confirmation Should Ask
    [Arguments]    ${message}
    Wait Until Element Is Visible    ${CONFIRM_DIALOG}
    Wait Until Element Text Is    ${CONFIRM_MESSAGE}    ${message}

Accept Confirmation
    Click Button    ${CONFIRM_YES}
    Wait Until Page Does Not Contain Element    ${CONFIRM_DIALOG}

Dismiss Confirmation
    Click Button    ${CONFIRM_NO}
    Wait Until Page Does Not Contain Element    ${CONFIRM_DIALOG}
