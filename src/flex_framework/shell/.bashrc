export PS1="\[\e[m\]\[\e[0;31m\]\$(echo "[\$FLEX_SHELL_PROXY_ENV_NAME]")\[\e[m\] $PS1"
export PS1="\[\e[m\]\[\e[0;31m\]\$(echo "[\$LPROJECT_NAME]")\[\e[m\] $PS1"

alias flex_reload="envsubst < ./env/.env.template > ./env/.env; exit 115"
alias switch_local="export FLEX_SHELL_PROXY_ENV_NAME=local; flex_reload"
alias switch_dev="export FLEX_SHELL_PROXY_ENV_NAME=dev; flex_reload"

if [ -n "$BASH_VERSION" ]; then
    if [ -f "./env/.bashrc" ]; then
        . "./env/.bashrc";
    fi
fi
