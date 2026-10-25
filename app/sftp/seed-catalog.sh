#!/bin/sh
# Runs at container start, after the SFTP user exists (atmoz/sftp executes scripts in /etc/sftp.d/).
# When the upload folder is a mounted volume it starts out owned by root, so hand it to the
# SFTP user, then copy in the sample catalog files that are not there yet.
for home in /home/*; do
  [ -d "$home/upload" ] || continue
  user=$(basename "$home")
  owner="$(id -u "$user"):$(id -g "$user")" || continue
  chown "$owner" "$home/upload"
  for f in /seed/*; do
    target="$home/upload/$(basename "$f")"
    if [ ! -e "$target" ]; then
      cp "$f" "$target"
      chown "$owner" "$target"
    fi
  done
done
