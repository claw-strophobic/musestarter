#!/bin/bash
find . -iname "*.py" | xargs xgettext -j --omit-header -d jackproject -o jackproject.pot -p ./pot/
cp -v ./pot/*.pot ./jackproject/locale/de/LC_MESSAGES/
cp -v ./pot/*.pot ./jackproject/locale/en/LC_MESSAGES/