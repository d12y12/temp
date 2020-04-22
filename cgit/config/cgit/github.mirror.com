#
# cgit config
# see cgitrc(5) for details

# Theme
css=/statics/cgit.css
logo=/statics/cgit.png
#logo-link=
favicon=/statics/favicon.ico
#footer=
#header=
head-include=/etc/cgitrc.d/head_option

# Filter
source-filter=/usr/lib/cgit/filters/syntax-highlighting.py
#source-filter=/usr/lib/cgit/filters/syntax-highlighting.sh
about-filter=/usr/lib/cgit/filters/about-formatting.sh

## Search for these files in the root of the default branch of repositories
## for coming up with the about page:
readme=:README.md
readme=:readme.md
readme=:README.mkd
readme=:readme.mkd
readme=:README.rst
readme=:readme.rst
readme=:README.html
readme=:readme.html
readme=:README.htm
readme=:readme.htm
readme=:README.txt
readme=:readme.txt
readme=:README
readme=:readme
readme=:INSTALL.md
readme=:install.md
readme=:INSTALL.mkd
readme=:install.mkd
readme=:INSTALL.rst
readme=:install.rst
readme=:INSTALL.html
readme=:install.html
readme=:INSTALL.htm
readme=:install.htm
readme=:INSTALL.txt
readme=:install.txt
readme=:INSTALL
readme=:install

## List of common mimetypes
mimetype.gif=image/gif
mimetype.html=text/html
mimetype.jpg=image/jpeg
mimetype.jpeg=image/jpeg
mimetype.pdf=application/pdf
mimetype.png=image/png
mimetype.svg=image/svg+xml
mimetype-file=/etc/mime.types

## General configuration
enable-commit-graph=1
enable-http-clone=1
enable-index-links=1
enable-log-filecount=1
enable-log-linecount=1
enable-remote-branches=1
enable-tree-linenumbers=1
enable-index-owner=1
enable-git-config=1
local-time=1
remove-suffix=1
max-stats=quarter
repository-sort=name
section-sort=1
case-sensitive-sort=1
snapshots=tar.gz tar.bz2 zip
robots=noindex, nofollow
agefile=info/web/last-modified

# Number of repos per page. Default value: "50".
max-repo-count=50
root-title=Mirror Repositories
root-desc=
virtual-root=/github

# Cache
cache-root=/var/cache/cgit/github
cache-size=1000

# Clone
#clone-prefix=
#clone-url=

# Auto scan
section-from-path=1
scan-path=/srv/git/

## List of repositories.
# include=/etc/$CGIT_REPO_LIST
