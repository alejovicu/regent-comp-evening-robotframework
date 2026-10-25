*** Settings ***
Documentation     Given / When / Then steps for the catalog feature.
...               Steps describe behaviour; the page objects know the locators.
Resource          ../resources/common.resource
Resource          ../resources/catalog_data.resource
Resource          ../pages/login_page.resource
Resource          ../pages/catalog_admin_page.resource
Resource          ../pages/product_form.resource
Resource          ../pages/confirm_dialog.resource
Resource          ../pages/shop_page.resource


*** Keywords ***
# ---------- Given ----------

The admin is on the catalog page
    Log In    ${ADMIN}[username]    ${ADMIN}[password]
    Catalog Admin Page Should Be Open

The shopper is on the shop page
    Log In    ${SHOPPER}[username]    ${SHOPPER}[password]
    Shop Page Should Be Open

Product "${sku}" named "${name}" priced "${price}" was added through the API
    Authenticate As    ${ADMIN}[username]    ${ADMIN}[password]
    Create Product    ${sku}    ${name}    ${price}

Product "${sku}" was deleted through the API
    Authenticate As    ${ADMIN}[username]    ${ADMIN}[password]
    Delete Product    ${sku}

# ---------- When: admin ----------

The admin adds the product
    [Arguments]    ${product}
    Click Add Product
    Product Form Should Be Open    Add product
    Fill Product Form    ${product}[sku]    ${product}[name]    ${product}[price]    ${product}[description]
    Save Product Form

The admin starts adding a product but cancels
    Click Add Product
    Product Form Should Be Open    Add product
    Fill Product Form    ${NEW_PRODUCT}[sku]    ${NEW_PRODUCT}[name]    ${NEW_PRODUCT}[price]
    Cancel Product Form

The admin opens product "${sku}" for editing
    Click Edit Product    ${sku}
    Product Form Should Be Open    Edit ${sku}

The admin changes it to name "${name}", price "${price}" and description "${description}"
    Fill Product Form    ${None}    ${name}    ${price}    ${description}
    Save Product Form

The admin asks to delete product "${sku}"
    Click Delete Product    ${sku}

The admin confirms
    Accept Confirmation

The admin changes their mind
    Dismiss Confirmation

# ---------- When: shopper ----------

The shopper searches for "${text}"
    Search Products    ${text}

The shopper clears the search
    Search Products    ${EMPTY}

The shopper opens the catalog management page
    Go To    ${CATALOG_URL}

# ---------- Then: admin ----------

The catalog should list ${count} products
    Catalog Should Show Product Count    ${count}

Product "${sku}" should be listed as "${name}" priced "${price}"
    Catalog Row Should Show    ${sku}    ${name}    ${price}

The new product should be listed
    [Arguments]    ${product}
    Catalog Row Should Show    ${product}[sku]    ${product}[name]    ${product}[display_price]    ${product}[description]

Product "${sku}" should not be listed
    Catalog Should Not Contain Product    ${sku}

The success message should be "${text}"
    Flash Message Should Be    success    ${text}

The form should be closed
    Product Form Should Be Closed

The form should show "${sku}", "${name}", "${price}" and "${description}"
    Product Form Should Show Values    ${sku}    ${name}    ${price}    ${description}

The SKU should not be editable
    SKU Field Should Be Read Only

The form should reject it with "${error}"
    Product Form Error Should Contain    ${error}

The confirmation should ask "${message}"
    Confirmation Should Ask    ${message}

# ---------- Then: shopper ----------

The shop should list ${count} products
    Shop Should List Product Count    ${count}

The shop should list only
    [Arguments]    @{skus}
    Shop Should List Only    @{skus}

The shop should show "${sku}" as "${name}" priced "${price}"
    Shop Row Should Show    ${sku}    ${name}    ${price}

The shop should show no products
    Shop Should Show No Products

The shop should not list "${sku}"
    Shop Should Not Contain Product    ${sku}

The shopper should be sent back to the shop
    Shop Page Should Be Open
    Catalog Admin Link Should Not Be Shown

# ---------- API ----------

The API is used by the shopper
    Authenticate As    ${SHOPPER}[username]    ${SHOPPER}[password]

The API is used without logging in
    Clear Authentication

Sending ${method} to the products endpoint should return ${status}
    [Arguments]    ${body}=${None}    ${sku}=${None}
    ${actual}=    Send Product Request    ${method}    sku=${sku}    body=${body}
    Should Be Equal As Integers    ${actual}    ${status}
    ...    msg=${method} /products returned ${actual}, expected ${status}

# ---------- Templates ----------

Adding a product is rejected
    [Documentation]    Data-driven check: the form keeps the error open and nothing is saved.
    [Arguments]    ${sku}    ${name}    ${price}    ${error}
    Open Catalog Admin Page
    Click Add Product
    Fill Product Form    ${sku}    ${name}    ${price}
    Save Product Form
    The form should reject it with "${error}"
    Cancel Product Form
    The catalog should list ${SEEDED_PRODUCT_COUNT} products
