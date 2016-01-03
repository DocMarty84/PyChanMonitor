# 4chan-download

## Server application

### Requirements

The server requires Python 3 (tested on version 3.4), and the 'non-usual' following modules:
- SQLAlchemy
- SQLite
- Flask
- Flask JSON-RPC (https://github.com/cenobites/flask-jsonrpc, available with `pip`)

### Configuration and use

The configuration must be done through a `config.py` file. A template is provided
(`config_template.py`), simply copy-paste to `config.py`, and fill in missing data.

The server application is split in two parts, a crawler (`main.py`) and a web server (`server.py`).
To use:
- define a crontab to run `cd <path_to_application> ; python3 main.py -a` on a regular basis
- launch `python3 server.py`, preferably in the background thanks to `screen`

Connect to the interface defined in the configuration.

## Android application

### Configuration

The configuration must be done directly in the file `app/www/index.html`. Set up the server endpoint
and the password (same than the one you defined in `config.py`).

### Build

The Android application requires the WebIntent plugin. To build, run the following in folder `app`:
- `cordova platform add android`
- `cordova plugin add https://github.com/florentvaldelievre/virtualartifacts-webIntent.git`
- `cordova build`

After the first build, a modification is necessary in the file
`app/platforms/android/AndroidManifest.xml`. Add the following to be able to make the application
appears when choosing the 'Share' option in Clover:
```xml
<intent-filter>
    <action android:name="android.intent.action.SEND" />
    <category android:name="android.intent.category.DEFAULT" />
    <data android:mimeType="text/plain" />
</intent-filter>
```

Build a second time to include the modification.
