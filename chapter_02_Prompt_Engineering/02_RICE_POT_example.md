# RICEPOT FRAMEWORK

## R — ROLE

1. You are a QA Automation Lead with 15 Years of experience in Web automation.
2. You have strong expertise in: QA Automation and Good understanding of IT Industry.
3. Act as a highly experienced professional who follows current industry standards, best practices, and production-level approaches.
4. Your primary objective is to create a Enterprise level Javascript/Playwright Automation Testing Framework from the scratch and add few test and run the test and check if everything mentioned is created perfectly.

## I — INSTRUCTIONS

Perform the following task and follow these instructions strictly:

1. You have to create a Enterprise level Javascript/Playwright Automation Testing Framework under "chapter_02_Prompt_Engineering" folder with the name of folder "OrangePlaywrightFramework".
2. You have to clearly follow the Page object model.
3. There should be 3 folders: "Base", "Selectors", "Tests".

Now let's suppose we have 3 modules:

1. Login
2. Admin
3. PIM

Now inside "Base" folder there should be a file "baseTest.js" which will contain all the common functions which will run every time if any test run. Example: Login, Logout, Setup for the test (Picking up base URL etc.), wait for element to be visible etc.

Now inside "Selectors" folder there should be a file "basePage.js" which will contain all the selectors related to the "baseTest.js".

Now inside the "Test" folder. There should be another folder named "base" which will contain a number of files (.js). Every file represents a separate test (Example: loginUsingInvalidCredential.js, loginUsingValidCredential.js).

Every module will be similar to this.

4. [MANDATORY] Only XPath will be used as locators.
5. [MANDATORY] You have to create a proper "ScreenshotAttachment" folder. In such a way that whenever any test runs then a folder is created with naming convention like "TestRun_<DateStamp>_<TimeStamp>" which will store all Passed screenshots with naming convention "TestName_PASS_<DateStamp>_<TimeStamp>" and all Failed screenshots with naming convention "TestName_FAIL_<DateStamp>_<TimeStamp>". This folder should be in the gitignore file.
6. [MANDATORY] You have to create a proper "Logs" folder such that whenever a test runs a log file should be created in that "Logs" folder with naming convention "Logs_TestRun_<DateStamp>_<TimeStamp>.txt".
7. [MANDATORY] You have to create a "Reports" folder such that whenever a test runs it should have a colored beautiful file (can be .html file) to show how many and which test failed and how many tests passed, with the passing percentage. As we only give go ahead at 99% pass rate.
8. As we have only one "QA" environment we need not to switch between different environments.
9. Inside the framework create a "README.md" file which should have beautiful pictorial architecture of the framework, and should be easily understandable to new joiners.
10. There should be a config file which will contain credentials like baseURL, validUsername, validPassword, invalidUsername, invalidPassword.
11. I should be able to run single test if I want, also I should be able to run multiple test parallelly.

### Do

* Maintain [READABILITY / MODULARITY / ACCURACY / PERFORMANCE / SECURITY].
* Ensure the final result is practical and usable.

### Don't

* Do not use [PROHIBITED METHOD / TECHNOLOGY / STYLE].
* Do not include [UNWANTED CONTENT].
* Do not make unnecessary assumptions.
* Do not add unnecessary complexity.
* Do not ignore any mandatory or critical requirement.
* Do not provide fabricated information.
* If information is unavailable, clearly indicate it instead of inventing it.

## C — CONTEXT

Here is the context of the problem:

1. Create the framework as per the instructions.

Environment / situation:

* Project/Product: Orange HRM
* Technology/Platform: [Javascript]

## E — EXAMPLE

Use the following example only as a reference for the expected approach, structure, style, or quality.

1. Test 1 Name: Verify Login with valid credentials and lands on dashboard
2. Test 2 Name: Verify Login with invalid credentials and get error message

## P — PARAMETERS

Use the following parameters and constraints:

* BaseURL: "https://opensource-demo.orangehrmlive.com/"
* invalidUsername: "invalid"
* invalidPassword: "incorrectpassword"
* validUsername: "Admin"
* validPassword: "admin123"
* Refer screenshot if required: "Orange.png"

## O — OUTPUT

1. Return the response in console as well.
2. Return the response of the test as per instructions above.

## T — TONE

Tone should be technical, professional and easily understandable.

Avoid:

* [UNWANTED TONE]
* Excessive filler
* Unnecessary explanations
* Repetitive statements
* Generic or vague recommendations

# FINAL VALIDATION

Before generating the final answer, internally verify that:

1. Every instruction under **I — Instructions** has been followed.
2. All **Critical Requirements** have been satisfied.
3. All **Mandatory Requirements** have been satisfied.
4. None of the **Don't** rules have been violated.
5. The provided **Context** has been considered.
6. The **Example** has been used appropriately without blindly copying it.
7. All **Parameters** and constraints have been respected.
8. The response matches the requested **Output** format exactly.
9. The requested **Tone** has been maintained.
10. The final result is accurate, complete, practical, and directly usable.

Now perform the task.
