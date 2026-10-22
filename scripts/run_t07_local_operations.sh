#!/bin/sh
# Install root-owned at /usr/local/sbin/shahab-t07-operations only after approval.
# Sudo must allow only this fixed wrapper to distinct unprivileged SSH users.
set -eu
umask 077

if [ "$(id -u)" != 0 ] || [ -z "${SUDO_UID:-}" ] || [ -z "${SUDO_USER:-}" ]; then
    echo "Local operator context is required." >&2
    exit 1
fi
if [ "$#" != 1 ]; then
    echo "Exactly one stage name is required." >&2
    exit 1
fi
case "$1" in
    01-import|02-review|03-prepare|04-approve|05-publish) stage=$1 ;;
    *) echo "Unrecognized stage." >&2; exit 1 ;;
esac

checkout=/home/shahab/t07-reviewed-checkout
policy=/etc/shahab/operations-operators.json
command_file=/etc/shahab/operations-commands/$stage.json
secret_file=/etc/shahab/operations-db.env
for file in "$policy" "$command_file" "$secret_file"; do
    [ -f "$file" ] && [ ! -L "$file" ] && [ "$(stat -c %u "$file")" = 0 ] || exit 1
    [ $((0$(stat -c %a "$file") & 022)) -eq 0 ] || exit 1
done
[ -d "$checkout" ] && [ ! -L "$checkout" ] && [ "$(stat -c %u "$checkout")" = 0 ] || exit 1
[ "$(stat -c %a "$secret_file")" = 600 ] || exit 1

cd /home/shahab/app
image=$(docker compose --env-file .env.prod -f docker-compose.prod.yml -p shahab-prod images -q api)
[ -n "$image" ] || exit 1
exec docker run --rm --read-only --cap-drop ALL --security-opt no-new-privileges \
    --network shahab-prod_data --tmpfs /tmp:rw,nosuid,noexec,size=32m \
    --env-file "$secret_file" --env SUDO_UID --env SUDO_USER \
    --mount "type=bind,src=$checkout,dst=/work,readonly" \
    --mount "type=bind,src=$policy,dst=/etc/shahab/operations-operators.json,readonly" \
    --mount "type=bind,src=$command_file,dst=/private/command.json,readonly" \
    --workdir /work --entrypoint python "$image" \
    -m scripts.operations_tool --local-ssh-operator --command /private/command.json
