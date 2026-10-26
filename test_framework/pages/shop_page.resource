*** Settings ***
Documentation     Page object: /shop (product catalog for shoppers)
Resource          ../resources/common.resource


*** Variables ***
${SHOP_URL}            ${BASE_URL}/shop
${SHOP_TITLE}          Product catalog
${SEARCH_INPUT}        id:search-input
${SHOP_ROWS}           css:#product-table tbody tr
${NO_PRODUCTS}         id:no-products
${NAV_CATALOG_ADMIN}   id:nav-products


*** Keywords ***
Open Shop Page
    Go To    ${SHOP_URL}
    Shop Page Should Be Open

Shop Page Should Be Open
    Wait Until Element Text Is    ${PAGE_TITLE}    ${SHOP_TITLE}

Search Products
    [Documentation]    Enters the term in one go. Typing it key by key can show stale
    ...    results: the page does not discard out-of-order search responses.
    [Arguments]    ${text}
    Set Input Value    ${SEARCH_INPUT}    ${text}

Shop Should List Product Count
    [Arguments]    ${count}
    Wait Until Element Count Is    ${SHOP_ROWS}    ${count}

Shop Should List Only
    [Arguments]    @{skus}
    ${count}=    Get Length    ${skus}
    Shop Should List Product Count    ${count}
    FOR    ${sku}    IN    @{skus}
        Page Should Contain Element    id:product-row-${sku}
    END

Shop Row Should Show
    [Arguments]    ${sku}    ${name}    ${price}
    Wait Until Element Text Is    id:product-name-${sku}     ${name}
    Wait Until Element Text Is    id:product-price-${sku}    ${price}

Shop Should Show No Products
    Wait Until Element Is Visible    ${NO_PRODUCTS}
    Page Should Not Contain Element    ${SHOP_ROWS}

Shop Should Not Contain Product
    [Arguments]    ${sku}
    Wait Until Page Does Not Contain Element    id:product-row-${sku}

Catalog Admin Link Should Not Be Shown
    Page Should Not Contain Element    ${NAV_CATALOG_ADMIN}
