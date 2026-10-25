*** Settings ***
Documentation     Page object: add / edit product dialog on the catalog page
Resource          ../resources/common.resource


*** Variables ***
${PRODUCT_FORM}            id:product-form
${PRODUCT_FORM_TITLE}      id:product-form-title
${PRODUCT_SKU}             id:product-sku
${PRODUCT_NAME}            id:product-name
${PRODUCT_PRICE}           id:product-price
${PRODUCT_DESCRIPTION}     id:product-description
${SAVE_PRODUCT}            id:save-product
${CANCEL_PRODUCT}          id:cancel-product
${PRODUCT_FORM_ERROR}      id:product-form-error


*** Keywords ***
Product Form Should Be Open
    [Arguments]    ${title}
    Wait Until Element Is Visible    ${PRODUCT_FORM}
    Wait Until Element Text Is    ${PRODUCT_FORM_TITLE}    ${title}

Product Form Should Be Closed
    Wait Until Page Does Not Contain Element    ${PRODUCT_FORM}

Fill Product Form
    [Documentation]    Fills the fields; ``sku`` is skipped when ``${None}`` (it is read-only on edit).
    [Arguments]    ${sku}    ${name}    ${price}    ${description}=${EMPTY}
    IF    $sku is not None    Fill Field    ${PRODUCT_SKU}    ${sku}
    Fill Field    ${PRODUCT_NAME}           ${name}
    Fill Field    ${PRODUCT_PRICE}          ${price}
    Fill Field    ${PRODUCT_DESCRIPTION}    ${description}

Save Product Form
    Click Button    ${SAVE_PRODUCT}

Cancel Product Form
    Click Button    ${CANCEL_PRODUCT}
    Product Form Should Be Closed

Product Form Should Show Values
    [Arguments]    ${sku}    ${name}    ${price}    ${description}
    Textfield Value Should Be    ${PRODUCT_SKU}            ${sku}
    Textfield Value Should Be    ${PRODUCT_NAME}           ${name}
    Textfield Value Should Be    ${PRODUCT_PRICE}          ${price}
    Textfield Value Should Be    ${PRODUCT_DESCRIPTION}    ${description}

SKU Field Should Be Read Only
    Element Should Be Disabled    ${PRODUCT_SKU}

Product Form Error Should Contain
    [Arguments]    ${expected}
    Wait Until Element Is Visible    ${PRODUCT_FORM_ERROR}
    Element Should Contain    ${PRODUCT_FORM_ERROR}    ${expected}
