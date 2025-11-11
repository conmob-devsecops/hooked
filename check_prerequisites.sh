#!/usr/bin/env bash
# AI generated script

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
RESET='\033[0m'

# Function to compare versions
version_compare() {
  if [[ $1 == "$2" ]]; then
    return 0
  fi
  local IFS=.
  local i ver1=($1) ver2=($2)
  # Fill empty positions with zeros
  for ((i = ${#ver1[@]}; i < ${#ver2[@]}; i++)); do
    ver1[i]=0
  done
  for ((i = 0; i < ${#ver1[@]}; i++)); do
    if [[ -z ${ver2[i]} ]]; then
      ver2[i]=0
    fi
    if ((10#${ver1[i]} > 10#${ver2[i]})); then
      return 1
    fi
    if ((10#${ver1[i]} < 10#${ver2[i]})); then
      return 2
    fi
  done
  return 0
}

# Initialize status
all_ok=true

echo "Checking prerequisites for hooked ..."
echo ""

echo -n "python:      "
MIN_PYTHON="3.12"
if command -v python3 &>/dev/null; then
  PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
  version_compare "$PYTHON_VERSION" "$MIN_PYTHON"
  result=$?
  if [[ $result -eq 2 ]]; then
    echo -e "${RED}✗${RESET} Required: ≥ ${MIN_PYTHON}, Found: ${PYTHON_VERSION}"
    all_ok=false
  else
    echo -e "${GREEN}✓${RESET} Required: ≥ ${MIN_PYTHON}, Found: ${PYTHON_VERSION}"
  fi
else
  echo -e "${RED}NOT INSTALLED${RESET} (Required: ≥${MIN_PYTHON})"
  all_ok=false
fi

echo -n "git:         "
MIN_GIT="2.9.0"
if command -v git &>/dev/null; then
  GIT_VERSION=$(git --version 2>&1 | awk '{print $3}')
  version_compare "$GIT_VERSION" "$MIN_GIT"
  result=$?
  if [[ $result -eq 2 ]]; then
    echo -e "${RED}✗${RESET} Required: ≥ ${MIN_GIT}, Found: ${GIT_VERSION}"
    all_ok=false
  else
    echo -e "${GREEN}✓${RESET} Required: ≥ ${MIN_GIT}, Found: ${GIT_VERSION}"
  fi
else
  echo -e "${RED}NOT INSTALLED${RESET} (Required: ≥ ${MIN_GIT})"
  all_ok=false
fi

echo -n "gitleaks:    "
MIN_GITLEAKS="8.28.0"
if command -v gitleaks &>/dev/null; then
  GITLEAKS_VERSION=$(gitleaks version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
  version_compare "$GITLEAKS_VERSION" "$MIN_GITLEAKS"
  result=$?
  if [[ $result -eq 2 ]]; then
    echo -e "${RED}✗${RESET} Required: ≥ ${MIN_GITLEAKS}, Found: ${GITLEAKS_VERSION}"
    all_ok=false
  else
    echo -e "${GREEN}✓${RESET} Required: ≥ ${MIN_GITLEAKS}, Found: ${GITLEAKS_VERSION}"
  fi
else
  echo -e "${RED}NOT INSTALLED${RESET} (Required: ≥ ${MIN_GITLEAKS})"
  all_ok=false
fi

# Check pre-commit
echo -n "pre-commit:  "
MIN_PRECOMMIT="4.0.0"
if command -v pre-commit &>/dev/null; then
  PRECOMMIT_VERSION=$(pre-commit --version 2>&1 | awk '{print $2}')
  version_compare "$PRECOMMIT_VERSION" "$MIN_PRECOMMIT"
  result=$?
  if [[ $result -eq 2 ]]; then
    echo -e "${RED}✗${RESET} Required: ≥ ${MIN_PRECOMMIT}, Found: ${PRECOMMIT_VERSION}"
    all_ok=false
  else
    echo -e "${GREEN}✓${RESET} Required: ≥ ${MIN_PRECOMMIT}, Found: ${PRECOMMIT_VERSION}"
  fi
else
  echo -e "${RED}NOT INSTALLED${RESET} (Required: ≥ ${MIN_PRECOMMIT})"
  all_ok=false
fi

echo ""

# Final summary
if $all_ok; then
  echo -e "${GREEN}All prerequisites OK${RESET}"
  exit 0
else
  echo -e "${RED}Some prerequisites are missing or outdated${RESET}"
  exit 1
fi
