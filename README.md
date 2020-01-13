# PyArmor Server

This is a simple webserver for PyArmor WebUI.

Start a web server on default port 9096 and open web browser:

    python server.py

Start on port 8089:

    python server.py -p 8089

No open web browser:

    python server.py -n

## API

### /version

Get version information of PyArmor, Server and Python

URL

    http://localhost:9096/version

Method: POST

Arguments: No

Success: HTTP/1.1 200 OK

Return

| Name       | Type    | Length | Description |
|------------|---------|--------|-------------|
| version    | String  |        | PyArmor version |
| regcode    | String  |        | PyArmor registration code, empty for trial version |
| reginfo    | String  |        | PyArmor registration name and email |
| server     | String  |        | PyArmor Server version |
| python     | String  |        | Python version |

For example

    {
    "version": "5.9.0",
    "regcode": "pyarmor-vax-00001",
    "reginfo": "jondy (jondy.zhao@*****.com)",
    "server": "0.1",
    "python": "3.7.0",
    }

### /register

Register PyArmor with key file

URL

    http://localhost:9096/register

Method: POST

Arguments: String, the key filename

Success: HTTP/1.1 200 OK

Return: Same as [/version](/version)

### /directory/list

List directories and files in this path

URL

    http://localhost:9096/directory/list

Method: POST

Arguments

| Name       | Type    | Required | Length | Description |
|------------|---------|----------|--------|-------------|
| path       | String  |    Y     |        | '@', '', '/', '/Users/jondy' |
| pattern    | String  |          |        | '*.py', filter the result files |

If path is `@`, return some favorite pathes, for example, User home
path, My Documents etc.

If path is empty, list the current path of PyArmor Server

Success: HTTP/1.1 200 OK

Return

| Name       | Type    | Length | Description |
|------------|---------|--------|-------------|
| path       | String  |        | Absolute path of request path |
| dirs       | List    |        | All the directories in this path |
| files      | List    |        | All the files matched the pattern in this path |

The list of `dirs` and `files` are sorted ignore case sensitivity.

For example

    {
      "path": "/Users/jondy",
      "dirs": [ "Desktop", "workspace" ],
      "files": []
    }

### /directory/new

Make a directory

URL

    http://localhost:9096/directory/new

Method: POST

Arguments: String, path to create

Success: HTTP/1.1 200 OK

Return: Absolute path created

### /directory/remove

Remove a directory

URL

    http://localhost:9096/directory/remove

Method: POST

Arguments: String, path to remove

Success: HTTP/1.1 200 OK

Return: Absolute path removed

### /project

Project Fields

| Name       | Type    |  NULL  | Description |
|------------|---------|--------|-------------|
| id         | Integer |   N    | Unique      |
| name       | String  |   N    |             |
| title      | String  |        |             |
| src        | String  |   N    | Base path for entry, include, exclude, plugin |
| entry      | List    |        | Entry scripts, relative src path |
| include    | Enum    |   N    | ("exact", "normal", "recursive") |
| exclude    | List    |        | Exclude pathes or scripts, default is empty list |
| buildTarget| Enum    |   N    | (0, 1, 2, 3) |
| output     | String  |        | Default is $src/dist |
| bundleName | String  |        | For pack, name bundle name. For obfuscate, package name |
| runtimeMode| Enum    |   N    | (0, 1, 2, 3) |
| plugins    | List    |        | Plugin script name, relatvie src path |
| licenseFile| String  |        | "true", "false" or absolute path of "license.lic" |
| platforms  | List    |        | For example, [ ['arm', 'linux.aarch32.0'], [...] ] |
| pack       | List    |        | Pack options, for example, ['--hidden-import', 'ctypes'] |
| bootstrapCode   | Enum    |   N    | (0, 1, 2, 3) |
| restrictMode    | Enum    |   N    | (0, 1, 2, 3, 4) |
| crossProtection | Boolean |   N    | Default is true |
| obfMod          | Boolean |   N    | Default is true |
| obfCode         | Boolean |   N    | Default is true |
| wrapMode        | Boolean |   N    | Default is true |
| advancedMode    | Boolean |   N    | Default is true |


#### /list

List all the projects

URL

    http://localhost:9096/project/list

Method: POST

Arguments: No

Success: HTTP/1.1 200 OK

Return:

A list of the project with all the fields

#### /new

Create a project

URL

    http://localhost:9096/project/new

Method: POST

Arguments:

All the project fields with `id` is empty

Success: HTTP/1.1 200 OK

Return:

All the project fields with `id` is set

###  /update

Update a project

URL

    http://localhost:9096/project/update

Method: POST

Arguments:

All the project fields with `id` must be set

Success: HTTP/1.1 200 OK

Return:

All the project fields

###  /remove

Remove a project

URL

    http://localhost:9096/project/remove

Method: POST

Arguments:

| Name       | Type    | Required | Length | Description |
|------------|---------|----------|--------|-------------|
| id         | Integer |    Y     |        | Project id  |
| clean      | Boolean |          |        | Remove the project path if set |

Success: HTTP/1.1 200 OK

Return:

All the project fields

####  /build

Build a project

URL

    http://localhost:9096/project/new

Method: POST

Arguments:

All the project fields.

If project `id` is empty, then create a temporary project

Success: HTTP/1.1 200 OK

Return: String, the final output path

### /license

License Fields:

| Name       | Type    |  NULL  | Description |
|------------|---------|--------|-------------|
| id         | Integer |   N    | Unique      |
| rcode      | String  |   N    |             |
| expired    | String  |        |             |
| harddisk   | String  |        |             |
| mac        | String  |        |             |
| ipv4       | String  |        |             |
| extraData  | String  |        |             |
| summary    | String  |        |             |
| filename   | String  |   N    | Readonly    |
| summary    | String  |        |             |
| disableRestrictMode | Boolean | | Unused |

#### /list

List all the licenses

URL

    http://localhost:9096/license/list

Method: POST

Arguments: No

Success: HTTP/1.1 200 OK

Return:

A list of the license files with all the fields

#### /new

Create a license

URL

    http://localhost:9096/license/new

Method: POST

Arguments:

All the license fields with `id`, `filename` are empty

Success: HTTP/1.1 200 OK

Return:

All the license fields with `id` and `filename` are set

###  /update

Update a license

URL

    http://localhost:9096/license/update

Method: POST

Arguments:

All the license fields with `id` must be set

Success: HTTP/1.1 200 OK

Return:

All the license fields

###  /remove

Remove a license

URL

    http://localhost:9096/license/remove

Method: POST

Arguments:

| Name       | Type    | Required | Length | Description |
|------------|---------|----------|--------|-------------|
| id         | Integer |    Y     |        | License id  |

Success: HTTP/1.1 200 OK

Return:

All the license fields

### /runtime

Not implemented

#### /list

#### /new

#### /update

#### /remove
