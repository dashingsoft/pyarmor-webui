# PyArmor-WebUI Robot Test Cases

Here are robot test cases to verify the main functions of pyarmor-webui, each
test case has one `.robot` file. These test cases also could be as a guide for
end users to understand how to use pyarmor-webui. Just install pyarmor-webui and
open it in the web browser:

    pip install pyarmor-webui
    pyarmor-webui

Then open any `.robot` file, run it by manual.

In order to run them automatically, first install `RobotFramework` and
`SeleniumLibrary` by `pip`

    pip install robotframework robotframework-seleniumlibrary

Then install one of browser drivers. The general approach to install a browser
driver is downloading a right driver, such as chromedriver for Chrome, and
placing it into a directory that is in `PATH`. Drivers for different browsers
can be found via [Selenium
documentation](https://selenium.dev/selenium/docs/api/py/index.html#drivers).

Now run any of one testcase

    robot generate_expired_license.robot

Or run the whole test suite

    robot pyarmor_webui_suite.robot

## Test Case List

* [Generate expired license](generate_expired_license.robot)
* [Gererate machine license](generate_machine_license.robot)
* [Generate extra data license](generate_extra_data_license.robot)

* [Obfuscate one script](pack_one_folder.robot)
* [Obfuscate multiple entries](pack_one_folder.robot)
* [Obfuscate high security script](pack_one_folder.robot)

* [Obfuscate one package](pack_one_folder.robot)
* [Obfuscate multiple packages](pack_one_folder.robot)

* [Obfuscate with local expired license](pack_one_folder.robot)
* [Obfuscate with internet expired license](pack_one_folder.robot)
* [Obfuscate with multiple mac license](pack_one_folder.robot)

* [Obfuscate cross platform](pack_one_folder.robot)
* [Obfuscate cross multiple platform](pack_one_folder.robot)

* [Pack one folder bundle](pack_one_folder.robot)
* [Pack one file bundle_with_license](pack_one_file_with_license.robot)
* [Pack one file bundle with outer license](pack_one_file_with_outer_license.robot)
* [Pack with new name, icon and data file](pack_with_name_icon_data_file.robot)
* [Pack high security script](pack_high_security_script.robot)
