# Optional: use this script to remove git lfs before update 1.2.2 to 1.3.0 if you have used git lfs in ymir before
# usage: ./remove_git_lfs.sh <path/to/ymir-workplace>

#!bash
set -e


remove_git_lfs_for_single_repo() {
    echo "checking $1"

    old=$PWD
    cd $1
    git config --global --add safe.directory $1

    # ignore all uncommited contents
    git checkout .
    git checkout master

    for bid in $(git for-each-ref --format='%(refname:short)' refs/heads/); do
        if [ ${#bid} -ne 30 ]; then continue; fi

        git checkout $bid

        if [ ! -f .gitattributes ]; then
            echo "skip: gitattributes not found"
            continue
        fi
        if grep -q lfs .gitattributes; then
            echo "disabling git lfs in $bid"
            echo "*.mir binary" > .gitattributes
            touch *.mir
            git add *.mir .gitattributes
            git commit -m 'remove git lfs'
        else
            echo "skip: lfs not found in gitattributes"
            continue
        fi
    done

    git lfs uninstall
    cd $old
}


main() {
    for uid in $(ls -1 $1/sandbox/); do
        if [ ${#uid} -ne 4 ]; then continue; fi
        for rid in $(ls -1 $1/sandbox/$uid); do
            if [ ${#rid} -ne 6 ]; then continue; fi
            remove_git_lfs_for_single_repo $1/sandbox/$uid/$rid
        done
    done
}

main "$@"
