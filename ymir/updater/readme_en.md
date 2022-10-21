## ymir-updater User's Guide

## Prepare for upgrade

1. Make sure the current running YMIR system version is 1.1.0 . ymir-updater does not support upgrades for other versions.
2. Make sure all training, mining and inference tasks in YMIR have been stopped, and then stop the ymir system: bash ymir.sh stop
It is recommended to back up the directory pointed to by YMIR_PATH in .env, the default is ymir-workplace in the YMIR code directory.
4. Check if you need enough hard disk space for the upgrade: If ymir-workplace takes 500G hard disk space, including 200G for ymir-assets, the rest will be automatically backed up during the upgrade. That is, at least 300G of additional space is needed for the upgrade.
Download the target version of YMIR and modify the .env file according to the configuration of the old version
In particular, MYSQL_INITIAL_USER and MYSQL_INITIAL_PASSWORD are copied directly from the old version. These old values are required to log in
6. If you are on an intranet, or on a network where you cannot connect to dockerhub, you need to get the upgrade image corresponding to the YMIR system first.
If you are using labelfree as a labeling job, please note the correspondence between LabelFree version and YMIR version, YMIR 2.0.0 system needs to run with 2.0.0 LabelFree image

## Upgrade operation

After confirming the above preparations, run bash ymir.sh update to upgrade and wait for the upgrade to complete

## FAQ

### 1. The upgrade script reports an error: sandbox not exists

Cause: The YMIR_PATH or BACKEND_SANDBOX_ROOT specified in .env is wrong, or there is . / symbol

Solution: Check the correctness of YMIR_PATH and BACKEND_SANDBOX_ROOT, and check whether their values appear . / symbols.

### 2. After upgrade, mongodb fails to start with an error: could not find mysql_initial_user xxxx

Cause: MYSQL_INITIAL_USER and MYSQL_INITIAL_PASSWORD in the .env file are not set according to the old version

Solution: Refer to Article 6 of the preparation

### 3. After the upgrade is completed, or when starting the system after rolling back from the backup, mysql fails to start and reports an error: No permission

Cause: When backing up ymir-workplace in step 3 of the preparation, the permissions of the ymir-workplace/mysql directory itself and its files may have been changed

Solution: sudo chown -R 27:sudo ymir-workplace/mysql
