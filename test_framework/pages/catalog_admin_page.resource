*** Settings ***
Documentation     Page object: /admin/products (catalog management, admin only)
Resource          ../resources/common.resource


*** Variables ***
${CATALOG_URL}             ${BASE_URL}/admin/products
${CATALOG_TITLE}           Catalog management
${ADD_PRODUCT_BUTTON}      id:add-product-button
${PRODUCT_COUNT}           id:product-count
${ADMIN_ROWS}              css:#admin-product-table tbody tr


*** Keywords ***
Open Catalog Admin Page
    Go To    ${CATALOG_URL}
    Catalog Admin Page Should Be Open

Catalog Admin Page Should Be Open
    Wait Until Element Text Is    ${PAGE_TITLE}    ${CATALOG_TITLE}
    Wait Until Element Is Visible    ${ADMIN_ROWS}

Click Add Product
    Click Button    ${ADD_PRODUCT_BUTTON}

Click Edit Product
    [Arguments]    ${sku}
    Click Button    id:edit-${sku}

Click Delete Product
    [Arguments]    ${sku}
    Click Button    id:delete-${sku}

Catalog Should Show Product Count
    [Arguments]    ${count}
    Wait Until Element Text Is    ${PRODUCT_COUNT}    ${count}
    Wait Until Element Count Is    ${ADMIN_ROWS}    ${count}

Catalog Row Should Show
    [Arguments]    ${sku}    ${name}    ${price}    ${description}=${None}
    ${row}=    Set Variable    css:#admin-product-table tr[data-sku="${sku}"]
    Wait Until Element Is Visible    ${row}
    Wait Until Element Text Is    ${row} .product-name    ${name}
    Wait Until Element Text Is    ${row} .product-price    ${price}
    IF    $description is not None
        Wait Until Element Text Is    ${row} .product-description    ${description}
    END

Catalog Should Not Contain Product
    [Arguments]    ${sku}
    Wait Until Page Does Not Contain Element    id:admin-row-${sku}
