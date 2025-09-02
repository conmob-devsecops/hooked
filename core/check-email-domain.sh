#!/usr/bin/env bash
# Copyright (C) 2025 T-Systems International GmbH.
#
# You can find the compulsory statement on:
# https://www.t-systems.com/de/en/compulsory-statement
#
# All rights, including licensing, inspection, modification and sharing of
# software and source code, reserved.

DEFAULT_ALLOWED_DOMAINS=(
  "telekom.de"
  "t-systems.com"
  "external.telekom.com"
  "external.t-systems.com"
)

extract_domain() {
  local email="$1"
  echo "${email##*@}"
}

validate_email() {
  local email="$1"
  if [[ $email =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
    return 0
  else
    return 1
  fi
}

check_domain() {
  local domain="$1"
  local domains_file="$2"

  if [[ -n "$domains_file" && -f "$domains_file" ]]; then
    while IFS= read -r allowed_domain; do
      [[ -z "$allowed_domain" || "$allowed_domain" =~ ^[[:space:]]*# ]] && continue
      allowed_domain=$(echo "$allowed_domain" | xargs)
      if [[ "$domain" == "$allowed_domain" ]]; then
        return 0
      fi
    done <"$domains_file"
  else
    for allowed_domain in "${DEFAULT_ALLOWED_DOMAINS[@]}"; do
      if [[ "$domain" == "$allowed_domain" ]]; then
        return 0
      fi
    done
  fi
  return 1
}

main() {
  local email="$(git config user.email)"

  if ! validate_email "$email"; then
    echo "Error: Invalid email format: $email"
    exit 1
  fi

  local domain=$(extract_domain "$email")

  if check_domain "$domain" "$domains_file"; then
    exit 0
  else
    exit 1
  fi
}

main
