Entry 1
- Student(s): Mustafa
- Artifact: backend/app/schemas/restaurant_request.py, backend/app/services/restaurant_service.py, backend/app/api/routes.py, backend/tests/test_restaurant_request.py
- Label: AI-ASSISTED
- AI tool: ChatGPT / Gemini
- Purpose: Help identify test cases, edge cases (length boundaries, blank/missing fields, duplicates), and structure repetitive testing patterns for restaurant creation and updating.
- Influence: Used the AI-suggested test structures and edge cases when writing and building the test suite. 
- Validation: Reviewed all generated test logic, manually verified coverage, and ran the full test suite and CI pipeline on every change.
- PR: #38, #41

Entry 2
- Student(s): Casey
- Artifact: backend/app/api/routes.py
- Label: AI-ASSISTED
- AI tool: ChatGPT
- Purpose: Implement fixes for making menu creation, updating, and deleting endpoints.
- Influence: Referenced and adapted the generated implementation to fix route logic.
- Validation: Manual checking, unit tests, and teammate review.
- PR: #39

Entry 3
- Student(s): Casey
- Artifact: backend/app/repositories/restaurant_repository.py
- Label: AI-ASSISTED
- AI tool: ChatGPT
- Purpose: Adding temporary files to prevent broken JSON and atomic saving.
- Influence: Referenced and adapted the generated implementation for atomic file replacement.
- Validation: Manual checking, unit tests, and teammate review.
- PR: #39

Entry 4
- Student(s): Casey
- Artifact: backend/app/services/restaurant_service.py, backend/app/api/routes.py
- Label: AI-GENERATED
- AI tool: ChatGPT
- Purpose: To debug errors while trying to make menu operations independent from `section_id`.
- Influence: Used and adapted the generated implementation to fix the routing and recursive service layer search logic.
- Validation: Manual checking, unit tests, and teammate review.
- PR: #39

Entry 5
- Student(s): Casey
- Artifact: backend/tests/test_menu_item_routes.py
- Label: AI-GENERATED
- AI tool: ChatGPT
- Purpose: Implement the JSON files and dummy data for testing the routes.
- Influence: Used and adapted the generated implementation to seed the test cases.
- Validation: Manual checking, unit tests, and teammate review.
- PR: #39

Entry 6
- Student(s): Casey
- Artifact: backend/tests/test_restaurant_service.py
- Label: AI-ASSISTED
- AI tool: ChatGPT
- Purpose: Explore approaches on how to implement testing for the service layer logic.
- Influence: Used the suggested approach when implementing the testing logic and assertions.
- Validation: Manual checking, unit tests, and teammate review.
- PR: #39

Entry 7
- Student(s): Nathan
- Artifact: backend/tests/test_restaurant_id_endpoint.py, backend/tests/test_restaurant_id_repository.py, backend/tests/test_restaurants_endpoint.py, backend/tests/test_restaurants_repository.py, backend/tests/test_restaurants_service.py
- Label: AI-ASSISTED
- AI tool: Gemini
- Purpose: Ensure correct test coverage and structure for all endpoints, service, and repository tests.
- Influence: Used the generated test cases and suggestions for tests.
- Validation: Manual checking, verified test coverage, ran the full test suite, and integrated via Pull Requests.
- PR: #40

Entry 8
- Student(s): Rameez
- Artifact: frontend/src/api/{request,fetchRestaurants,fetchRestaurantDetails,createRestaurant,updateRestaurant,createMenuItem,updateMenuItem,deleteMenuItem}.ts; frontend/src/components/restaurant_management_page/{GeneralManagement,MenuManagement}.tsx; frontend/src/components/restaurant_page/MenuItemCard.tsx; frontend/src/pages/{DiscoverPage,RestaurantPage,RestaurantSelectPage,CreateRestaurantPage,RestaurantManagementPage}.tsx; frontend/src/schemas/{restaurant,menu,menu_section}.d.ts; frontend/vite.config.ts
- Label: AI-ASSISTED
- AI tool: Codex
- Purpose: Build the restaurant management and menu management interfaces, connect frontend screens to API.
- Influence: Codex generated and revised the menu editor and integrated API functions. 
- Validation: Manual checking, teammate review.

- Entry 9
- Student(s): Mustafa
- Artifact: backend/tests/testcustomer.py, testcart.py, test_json_repository.py, test_customer_to_order_workflow.py, test_checkout_service.py
- Label: AI-Assisted
- AI tool: Claude (Claude Code)
- Purpose: Write tests for customers, cart and checkout, including the Customer -> Menu -> Cart -> Checkout -> Order integration test.
- Influence: helped write  tests ; removed duplicate tests and fixed tests, identified edgee cases
- Validation: Checked that breaking each business rule makes a test fail, ran the suite in CI.
- PR: #70, #76, #86

Entry 10
- Student(s): Nathan
- Artifact: test_auth_endpoints, test_cart_endpoints_with_token
- Label: AI-ASSISTED
- AI tool: Gemini
- Purpose: To ensure new tests are made with new auth system
- Influence: Used the generated test cases and suggestions for tests specifically with auth, making sure all edge cases are covered.
- Validation: Manual checking, verified test coverage, ran the full test suite, and integrated via Pull Requests.
- PR: #40

Entry 11
- Student(s): Casey
- Artifact: backend/app/tests/test_checkout_routes.py; backend/app/tests/test_checkout_service.py; backend/app/tests/conftest.py
- Label: AI-ASSISTED
- AI tool: ChatGPT
- Purpose: Implement sample data for testing; Explore approach and structure on how to implement the testings, as well as debugging and expanding coverage
- Influence: Adapted the generated testing sample data, as well as the logic
- Validation: Manual checking, unit tests, and teammate review
- PR: #85

Entry 12
- Student(s): Casey
- Artifact: backend/app/services/cart_service.py; backend/app/services/cart_pricing.py; backend/app/services/checkout_serivice.py
- Label: AI-ASSISTED
- AI tool: ChatGPT
- Purpose: Clean up duplicated cart pricing logic and unused helpers
- Influence: Applied the suggested fixes
- Validation: Manual checking, unit tests, and teammate review
- PR: #87

Entry 13
- Student(s): Casey
- Artifact: backend/app/api/routes.py
- Label: AI-GENERATED
- AI tool: ChatGPT
- Purpose: To implement trials and error messages
- Influence: Used and adapted the generated implementation.
- Validation: Manual checking, unit tests, and teammate review
- PR: #85