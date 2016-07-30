# Gentoo Update

Update gentoo system automatically, kernel configuration was build as if the
keyboard key "Enter" was pressed repeatedly.

Notes:

* you have to resolve emerge conflicts yourself.
* parallel jobs execution is the default, to disable use the parameter
  `./main.py waf ' --jobs=1 build'`, notice the added space after the first
  single quote.
* to see all available waf options, run `./main.py waf ' --help'`.

ToDo: send email if emerge failed.


## Installation

1. Create your own copy of `wscript`, look at example in
   `wscript.example`.

2. Create your own copy of `build_rules.yml`, look at example in
   `build_rules.yml.example`.

3. Run `./configure.sh`

4. You need `argh` installed as global python library (installed
   as root).


## Usage

1. Update portage (rsync) yourself, build can start when the timestamp changed.

2. Run `./main.py waf build`


## Changelog

None
