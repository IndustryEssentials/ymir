
# Typical test cases for a single mir command

* for mir itself:
  * `mir`
  * `mir --version` and `mir -v`
  * `mir --help` and `mir -h`
* for each sub command:
  * `mir <command> -h`
  * `mir <command> --help`
  * `mir <command> <args>`, this script should run in the following cases:
    * inside root dir of a mir repo
      * inside sub dirs, for example: .git or .dvc, of a mir repo
    * outside a mir repo
    * inside a pure git repo (maybe it's from another project)

* To run all tests:
* run: cd tests && python __main__.py
