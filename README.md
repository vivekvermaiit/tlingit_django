This is the repository for tools over Tlingit corpus: https://github.com/jcrippen/tlingit-corpus

There is a Django app that can be run locally. For distribution, the Django app is packaged with pyinstaller, and then run inside Electron to create a web app.

The app is available for Mac OS and Linux. 

The database used is SQLite and you would benefit from having a GUI tool to view the database, such as DB Browser for SQLite: https://sqlitebrowser.org/

## To get the app running locally for development:

1. Clone the repository
2. Create a virtual environment and install the dependencies. Run this in tlignit_django/

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
3. Run migrations in tlingit_django/tlingit_app

```
python manage.py migrate
```

4. Seed the DB:
```
python manage.py seed_corpus
```

5. Run the server:
```
python manage.py runserver
```

You will be able to access the homepage after this on:
http://127.0.0.1:8000/corpus/lines/

After you've run this at least once, the next times you want to run the server (from tlingit_django):

```
source venv/bin/activate
cd tlingit_app
python manage.py runserver
```

## Updating tags locally from source

We use a separate github repo to synchronize the tags on Tlingit text. To sync your local DB with the latest tags, 
download the tags.json from here:
https://github.com/vivekvermaiit/tlingit_corpus_data

Then run application and use the "Export/Import Tlingit Tags" feature on main page to import the tags. 

## Packaging Instructions:

### For Mac OS:

We support both Intel and Apple Silicon Macs. So the build process will create a universal binary that can run on both types of machines.
We need to create two separate binaries for the Django app with pyinstaller, and a single electron app that combines both. 

First we use pyinstaller to create an executable of the Django app. 

#### Pyinstaller for Apple Silicon:
To get pyinstaller package (run this in tlingit_app):

```
pyinstaller --onefile manage.py --name tlingit_backend \
  --add-data "corpus/templates:corpus/templates" \
  --add-data "corpus/static:corpus/static" \
  --add-data "corpus/templatetags:corpus/templatetags" \
  --add-data "db.sqlite3:."
```

You can run this to see if everything is working:

```
./dist/tlingit_backend runserver --noreload
```

#### Pyinstaller for Intel:

Next we create this on Intel architecture with Rosetta:

On a new terminal window, switch to Intel shell via Rosetta
```
arch -x86_64 zsh
```

Verify
```
arch  # should print i386
```

Install x86_64 Homebrew if you don't have it. (x86 homebrew installs to /usr/local (not /opt/homebrew))
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Install Python
```
/usr/local/bin/brew install python
```


Create x86 venv (from tlingit_django/)
```
/usr/local/bin/python3 -m venv venv_x86
source venv_x86/bin/activate
```

Install dependencies
```
pip install -r requirements.txt
```

To get pyinstaller package (run this in tlingit_app):
```
pyinstaller --onefile manage.py --name tlingit_backend \
  --add-data "corpus/templates:corpus/templates" \
  --add-data "corpus/static:corpus/static" \
  --add-data "corpus/templatetags:corpus/templatetags" \
  --add-data "db.sqlite3:." \
  --distpath "dist_x86"
```

You can run this with:
```
./dist_x86/tlingit_backend runserver --noreload
```

#### Electron App:

To package this inside an Electron app. The app needs to be signed and notarized to be able to run on other laptops. 

Firstly get the apple certificate and double .p12 file and enter pwd. It will import it to your keychain.

In the package.json file update the "identity" field with the name of the certificate and update the version number of the app. 


To build electron (tlingit_django/electron):

```
export APPLE_ID=""
export APPLE_ID_PASSWORD=""
export APPLE_TEAM_ID=""
export APPLE_APP_SPECIFIC_PASSWORD=""
npm run build
```

To open the app:
```
open "../dist_electron/mac-universal/Tlingit App.app"
```

To notorize the dmg for sharing

from tlingit_django/dist_electron
```
codesign --sign "Developer ID Application: xx (xxx)" \
  "Tlingit App-1.0.0-universal.dmg"
```

Submit the file for notarization.
```
xcrun notarytool submit "Tlingit App-1.0.0-universal.dmg" \
  --apple-id "" \
  --password "" \
  --team-id ""
```

Check status of notarization:
```
xcrun notarytool history \
  --apple-id "" \
  --password "" \
  --team-id ""
```
Once notarized, staple:
```
xcrun stapler staple "Tlingit App-1.0.0-universal.dmg"
```

Post this, dmg can be shared. 


### For Linxux version

Have docker installed on your machine and start it. 

from tlingit_app:
```
./build_linux.sh
```

From (tlingit_django/electron):
```
docker run --platform linux/amd64 \
  -v "$(pwd)":/app \
  -v "$(pwd)/../tlingit_app/dist":/tlingit_app/dist \
  -v "$(pwd)/../dist_electron":/dist_electron \
  -w /app \
  node:20 bash -c "
    npm install &&
    npm run build -- --linux
  "
```

## Tagging flow 

To make changes to tags, follow this process:

1) Before starting your updates, pull latest tag file from github
2) Import this file using the Import button
3) Make your changes.
4) Export the tag file and upload to github.

