# PyArmor-WebUI Robot Test Cases

Here are robot test cases to verify the main functions of pyarmor-webui, each
test case has one `.robot` file. These test cases also could be as a guide for
end users to understand how to use pyarmor-webui. Just install pyarmor-webui and
start it:

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

Start pyarmor-webui at port 9096, the port must be same as specified
in the [resource.robot](resource.robot]:

    pyarmor-webui -p 9096 -n

Now run any of one testcase. For example

    robot generate_expired_license.robot

Or run the whole test suite

    robot .

## Test Case List

* [Generate expired license](generate_expired_license.robot)
* [Gererate machine license](generate_machine_license.robot)
* [Generate extra data license](generate_extra_data_license.robot)

* [Obfuscate one script](obfuscate_one_script.robot)
* [Obfuscate multiple entries](obfuscate_multiple_entries.robot)
* [Obfuscate one package](obfuscate_one_package.robot)

* [Pack one folder bundle](pack_one_folder_bundle.robot)
* [Pack one file bundle](pack_one_file_bundle.robot)
* [Pack one file bundle with outer license](pack_one_file_with_outer_license.robot)
* [Pack with data_file](pack_with_data_file.robot)

## References

* [RobotFramework User Guide](http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html)
