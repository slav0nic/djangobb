## What is DjangoBB?

DjangoBB is a quick and simple forum which uses the Django Framework (written in Python language).
Abbreviation DjangoBB stands for **Django** **B**ulletin **B**oard.
DjangoBB is distributed under the BSD license.

[![](https://pledgie.com/campaigns/16554.png?skin_name=chrome)](http://pledgie.com/campaigns/16554)
[![](http://api.flattr.com/button/flattr-badge-large.png)](http://flattr.com/thing/93067/DjangoBB-Django-based-forum)
[![](http://www.openhub.net/p/djangobb/widgets/project_thin_badge.gif)](http://www.openhub.net/p/djangobb?ref=sample)
[![](https://drone.io/bitbucket.org/slav0nic/djangobb/status.png)](https://drone.io/bitbucket.org/slav0nic/djangobb/latest)
[![](https://codecov.io/bitbucket/slav0nic/djangobb/coverage.svg?branch=default)](https://codecov.io/bitbucket/slav0nic/djangobb?branch=default)
[![](http://requires.io/bitbucket/slav0nic/djangobb/requirements.svg?branch=default)](http://requires.io/bitbucket/slav0nic/djangobb/requirements/?branch=default)
[![](https://img.shields.io/badge/irc-freenode-blue.svg)](https://webchat.freenode.net/?channels=djangobb)


## The basic concept of the forum progress is:

 * the usage of various DBMS (MySQL, PostgreSQL, Oracle, SQLite)
 * the ease of integration into any Django project and the ease of installation
 * the usage of standard libraries for launching on conventional hostings with python support
 * user-friendly installation process
 * classic view of the forum like IPB, PhpBB, Punbb
 * easy forum setup
 * high speed
 * reliability

At the current stage of development the main object is the functional implementation of the PunBB forum, in the sequel it is projected to expand it significantly.

## Documentation

Will be soon...

### Install
DjangoBB consists of 2 parts:

 * [main app](http://bitbucket.org/slav0nic/djangobb)
 * [basic project](http://bitbucket.org/slav0nic/djangobb_project) (example of usage for quick install)


#### Compatibility
  * Python **2.7/3.3+**
  * Django >= **1.8**

Fore more info pls check ''requirements.txt'' and ''optional-requirements.txt'' files

#### Preinstall requiments:

* virtualenv
* setuptools or pip

#### Download latest source and install app:

```
#!sh
 wget https://bitbucket.org/slav0nic/djangobb/get/stable.tar.gz
 tar zxvf stable.tar.gz
 virtualenv .env
 cd <place_for_virtualenv_dir>
 source .env/bin/activate
 # setup.py from djangobb app
 ./setup.py install
 # ./setup.py develop will be ok too if you are planning to upgrade djangobb from hg

```

Download and setup basic project:

```
#!sh
 wget https://bitbucket.org/slav0nic/djangobb_project/get/tip.tar.gz
 tar zxvf tip.tar.gz
 cd slav0nic-djangobb_project-tip/
 pip install -r requirements.txt
 cd basic_project/
 touch local_settings.py
 # set DATABASE
 ./manage.py migrate
 ./manage.py collectstatic
 ./manage.py runserver
```

Also you can add djangobb_forum to your django project as app and install requirements via pip.


## User Support and demo
`#djangobb` on freenode IRC

Forum:
[support.djangobb.org](http://support.djangobb.org/)

Mercurial repository: [https://bitbucket.org/slav0nic/djangobb/](https://bitbucket.org/slav0nic/djangobb/)
Git mirror: [http://github.com/slav0nic/DjangoBB/](http://github.com/slav0nic/DjangoBB/)

## Migration from other forum engines:

''will be soon...''

[punBB-to-DjangoBB](http://github.com/Kami/punBB-to-DjangoBB) ''unofficial/inactive''

[phpBB3 to DjangoBB](https://github.com/jedie/django-phpBB3) ''unofficial''

## "Why another forum?"

As far`as we are concerned, there is no usable engine written in Django. In our humble opinion, existing implementations are too simple and have little function.

## Sites using DjangoBB
[DjangoBBPowered](https://bitbucket.org/slav0nic/djangobb/wiki/DjangoBBPowered)

## Development

### Translation:
http://www.transifex.net/projects/p/djangobb/

![translation progress](http://www.transifex.net/projects/p/djangobb/resource/default/chart/image_png)

[Howto add new translation?](https://bitbucket.org/slav0nic/djangobb/wiki/HowtoAddNewTranslation)
