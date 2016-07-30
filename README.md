# Gentoo Update

Update gentoo system automatically, kernel configuration was build as if the
keyboard key "Enter" was pressed repeatedly.

Note: you have to resolve emerge conflicts yourself.

ToDo: send email if emerge failed.


## Installation

1. Run `./configure.sh`

2. Create your own copy of `build_rules.yml`, look at example in
   `build_rules.yml.example`.


## Usage

1. Update portage (rsync) yourself, build can start when the timestamp changed.

2. Run `./main.py waf build`
