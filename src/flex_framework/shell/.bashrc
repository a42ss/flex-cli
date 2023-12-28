before_flex_reload(){
    lcli helper cache_clear
    if [ -f ./env/bash_proxy_meta.json ]; then
        lcli string -f ./env/bash_proxy_meta.json remove_new_lines  print_env -e ./env/.env.template -v FLEX_BASH_PROXY_META
    fi
}

after_flex_reload() {
    mkdir -p .flex-cli/cache/bin/bash_completion.d
    echo "PATH=\"${PATH}\"" > .flex-cli/cache/bin/PATH-original.env
    lcli -- --completion >> .flex-cli/cache/bin/bash_completion.d/lcli-bash-completion.sh
    lcli lproject -- --completion >> .flex-cli/cache/bin/bash_completion.d/lproject-bash-completion.sh
}

flex_reload() {
    EXIT_CODE="$1"
    before_flex_reload
    envsubst < ./env/.env.template > ./env/.env
    if [ -n "${EXIT_CODE}" ]; then
        exit ${EXIT_CODE}
    else
        exit 115
    fi
}
switch_env() {
    ENVIRONMENT="$1"
    EXIT_CODE="$2"
    if [ -n "${ENVIRONMENT}" ]; then
        echo "Switching to $ENVIRONMENT ..."
        export FLEX_SHELL_PROXY_ENV_NAME="$ENVIRONMENT"
        export FLEX_RELOAD_FLAG="True"
        flex_reload 0
    fi
}

if [ -n "$FLEX_FIRST_COMMAND" ]; then
    eval "${FLEX_FIRST_COMMAND}"
    unset FLEX_FIRST_COMMAND
fi

shopt -s expand_aliases
export FLEX_CLI=true

if [ -n "$FLEX_RELOAD_FLAG" ]; then
    flex_reload
else
    before_flex_reload
fi
after_flex_reload

export PS1="\[\e[m\]\[\e[0;31m\]\$(echo "[\$FLEX_SHELL_PROXY_ENV_NAME]")\[\e[m\] $PS1"
export PS1="\[\e[m\]\[\e[0;31m\]\$(echo "[\$LPROJECT_NAME]")\[\e[m\] $PS1"

alias switch_local="export FLEX_SHELL_PROXY_ENV_NAME=local; flex_reload"
alias switch_dev="export FLEX_SHELL_PROXY_ENV_NAME=dev; flex_reload"

if [ -n "$BASH_VERSION" ]; then
    if [ -f "./env/.bashrc" ]; then
        . "./env/.bashrc";
    fi
fi

# source compat completion directory definitions
compat_dir=${FLEX_BASH_COMPLETION_COMPAT_DIR:-./.flex-cli/cache/bin/bash_completion.d}
if [[ -d $compat_dir && -r $compat_dir && -x $compat_dir ]]; then
    for i in "$compat_dir"/*; do
        [[ ${i##*/} != @($_backup_glob|Makefile*|$_blacklist_glob) && -f \
        $i && -r $i ]] && . "$i"
    done
fi
unset compat_dir i _blacklist_glob

