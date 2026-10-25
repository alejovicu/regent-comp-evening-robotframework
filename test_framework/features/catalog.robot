*** Settings ***
Documentation     Feature: Catalog
...
...               As an admin I manage the products in the catalog (add, edit, delete),
...               and as a shopper I browse and search the products I can buy.
...               Every test starts from the 6 sample products.
Resource          ../specs/catalog_steps.resource
Suite Setup       Start Test Session
Suite Teardown    End Test Session
Test Setup        Restore Demo Data
Test Tags         catalog


*** Test Cases ***
# ---------- Admin: catalog management ----------

Admin sees the sample catalog
    [Tags]    admin    smoke
    Given the admin is on the catalog page
    Then the catalog should list 6 products
    And product "MUG-001" should be listed as "Coffee Mug" priced "$9.50"
    And product "KEYB-001" should be listed as "Mechanical Keyboard" priced "$89.00"

Admin adds a product
    [Tags]    admin    smoke
    Given the admin is on the catalog page
    When the admin adds the product    ${NEW_PRODUCT}
    Then the success message should be "Product CAP-001 created"
    And the form should be closed
    And the new product should be listed    ${NEW_PRODUCT}
    And the catalog should list 7 products

Admin cancels adding a product
    [Tags]    admin
    Given the admin is on the catalog page
    When the admin starts adding a product but cancels
    Then product "CAP-001" should not be listed
    And the catalog should list 6 products

Admin cannot add an invalid product
    [Tags]    admin    validation
    [Setup]    Run Keywords    Restore Demo Data    AND    Given the admin is on the catalog page
    [Template]    Adding a product is rejected
    # sku          name             price       error shown in the form
    BAD SKU        Thing            5           sku: String should match pattern
    ${EMPTY}       Thing            5           sku: String should have at least 1 character
    NEW-001        ${EMPTY}         5           name: String should have at least 1 character
    NEW-001        Thing            0           price: Input should be greater than 0
    NEW-001        Thing            -3          price: Input should be greater than 0
    NEW-001        Thing            ${EMPTY}    price: Input should be a valid number
    MUG-001        Another mug      5           SKU MUG-001 already exists

Admin edits a product
    [Tags]    admin    smoke
    Given the admin is on the catalog page
    When the admin opens product "MUG-001" for editing
    Then the form should show "MUG-001", "Coffee Mug", "9.5" and "Ceramic mug, 350 ml"
    And the SKU should not be editable
    When the admin changes it to name "Travel Mug", price "12.3" and description "Steel, 450 ml"
    Then the success message should be "Product MUG-001 updated"
    And product "MUG-001" should be listed as "Travel Mug" priced "$12.30"
    And the catalog should list 6 products

Admin cannot save an edit with an invalid price
    [Tags]    admin    validation
    Given the admin is on the catalog page
    When the admin opens product "MUG-001" for editing
    And the admin changes it to name "Coffee Mug", price "0" and description "Ceramic mug, 350 ml"
    Then the form should reject it with "price: Input should be greater than 0"

Admin deletes a product
    [Tags]    admin    smoke
    Given the admin is on the catalog page
    When the admin asks to delete product "MUG-001"
    Then the confirmation should ask "Delete Coffee Mug (MUG-001)?"
    When the admin confirms
    Then the success message should be "Product MUG-001 deleted"
    And product "MUG-001" should not be listed
    And the catalog should list 5 products

Admin keeps a product when cancelling the delete
    [Tags]    admin
    Given the admin is on the catalog page
    When the admin asks to delete product "MUG-001"
    And the admin changes their mind
    Then product "MUG-001" should be listed as "Coffee Mug" priced "$9.50"
    And the catalog should list 6 products

# ---------- Shopper: browsing and searching ----------

Shopper browses the catalog
    [Tags]    shopper    smoke
    Given the shopper is on the shop page
    Then the shop should list 6 products
    And the shop should show "MUG-001" as "Coffee Mug" priced "$9.50"

Shopper searches by name ignoring case
    [Tags]    shopper    search
    Given the shopper is on the shop page
    When the shopper searches for "coffee"
    Then the shop should list only    MUG-001

Shopper searches by SKU
    [Tags]    shopper    search
    Given the shopper is on the shop page
    When the shopper searches for "keyb"
    Then the shop should list only    KEYB-001

Shopper search matches several products
    [Tags]    shopper    search
    Given the shopper is on the shop page
    When the shopper searches for "M"
    Then the shop should list only    BOOK-001    MUG-001    KEYB-001    MOUSE-001

Shopper search without matches
    [Tags]    shopper    search
    Given the shopper is on the shop page
    When the shopper searches for "unicorn"
    Then the shop should show no products

Shopper clears the search
    [Tags]    shopper    search
    Given the shopper is on the shop page
    And the shopper searches for "coffee"
    When the shopper clears the search
    Then the shop should list 6 products

Shopper sees products the admin adds
    [Tags]    shopper    api
    Given product "CAP-001" named "Robot Cap" priced "15.5" was added through the API
    And the shopper is on the shop page
    Then the shop should list 7 products
    And the shop should show "CAP-001" as "Robot Cap" priced "$15.50"

Shopper no longer sees products the admin deletes
    [Tags]    shopper    api
    Given product "MUG-001" was deleted through the API
    And the shopper is on the shop page
    Then the shop should list 5 products
    And the shop should not list "MUG-001"

# ---------- Access control ----------

Shopper cannot open catalog management
    [Tags]    shopper    security
    Given the shopper is on the shop page
    When the shopper opens the catalog management page
    Then the shopper should be sent back to the shop

Shopper cannot change the catalog through the API
    [Tags]    api    security
    Given the API is used by the shopper
    Then sending GET to the products endpoint should return 200
    And sending POST to the products endpoint should return 403
    ...    body={"sku": "HACK-001", "name": "Nope", "price": 1}
    And sending PUT to the products endpoint should return 403
    ...    sku=MUG-001    body={"name": "Nope", "price": 1}
    And sending DELETE to the products endpoint should return 403    sku=MUG-001

Catalog requires logging in
    [Tags]    api    security
    Given the API is used without logging in
    Then sending GET to the products endpoint should return 401
