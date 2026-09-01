#!/usr/bin/env bash
# Usage: ./tools/audit-harness.sh [path-al-proyecto]
# Uses jq when available for strict JSON validation; otherwise falls back to a
# small awk/sed parser for the pretty-printed feature_list.json used here.

set -eu

if [ -t 1 ]; then
  RED="$(printf '\033[31m')"; YELLOW="$(printf '\033[33m')"
  GREEN="$(printf '\033[32m')"; RESET="$(printf '\033[0m')"
else
  RED=""; YELLOW=""; GREEN=""; RESET=""
fi

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
ROOT_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
HAS_JQ=0; command -v jq >/dev/null 2>&1 && HAS_JQ=1

PROJECTS_TOTAL=0
FEATURES_OK=0
FEATURES_PROBLEMS=0
GLOBAL_CRITICAL=0
FOUND_FEATURE_LIST=0
TMP_ROOT="${TMPDIR:-/tmp}/audit-harness.$$"
mkdir -p "$TMP_ROOT"
trap 'rm -rf "$TMP_ROOT"' EXIT HUP INT TERM

JQ_FEATURE='if type=="array" then .[$i] elif (.features|type)=="array" then .features[$i] else empty end'

add_critical() {
  GLOBAL_CRITICAL=$((GLOBAL_CRITICAL + 1))
  printf '%s\t%s\t%s\n' "$1" "$2" "$3" >> "$4"
}

add_recommended() {
  printf '%s\t%s\t%s\n' "$1" "$2" "$3" >> "$4"
}

print_findings() {
  level="$1"; file="$2"; color="$3"; symbol="$4"
  printf '%s%s%s\n' "$color" "$level" "$RESET"
  if [ ! -s "$file" ]; then
    printf '%s[OK]%s sin findings\n' "$GREEN" "$RESET"
    return
  fi
  while IFS="$(printf '\t')" read -r fid fname msg; do
    [ -n "$fid$msg" ] || continue
    printf '%s%s%s feature %s/%s: %s\n' "$color" "$symbol" "$RESET" "$fid" "$fname" "$msg"
  done < "$file"
}

json_valid() {
  file="$1"
  if [ "$HAS_JQ" -eq 1 ]; then
    jq empty "$file" >/dev/null 2>&1
    return $?
  fi
  awk '
    BEGIN { dq=0; esc=0; bc=0; br=0 }
    {
      for (i=1; i<=length($0); i++) {
        c=substr($0,i,1)
        if (dq) {
          if (esc) { esc=0; continue }
          if (c=="\\") { esc=1; continue }
          if (c=="\"") dq=0
          continue
        }
        if (c=="\"") dq=1
        else if (c=="{") bc++
        else if (c=="}") bc--
        else if (c=="[") br++
        else if (c=="]") br--
        if (bc<0 || br<0) bad=1
      }
    }
    END { exit (bad || dq || bc!=0 || br!=0) ? 1 : 0 }
  ' "$file" >/dev/null 2>&1
}

feature_count() {
  file="$1"
  if [ "$HAS_JQ" -eq 1 ]; then
    jq 'if type=="array" then length elif (.features|type)=="array" then (.features|length) else 0 end' "$file"
    return
  fi
  awk '
    BEGIN { inarr=0; obj=0; count=0 }
    /^[[:space:]]*\[/ { if (!inarr) inarr=1; next }
    /^[[:space:]]*"features"[[:space:]]*:/ { inarr=1; next }
    inarr && obj==0 && /^[[:space:]]*{[[:space:]]*$/ { count++; obj=1; next }
    inarr && obj>0 {
      for (i=1; i<=length($0); i++) {
        c=substr($0,i,1); if (c=="{") obj++; if (c=="}") obj--
      }
    }
    END { print count }
  ' "$file"
}

extract_feature() {
  file="$1"; one_based="$2"; out="$3"
  awk -v want="$one_based" '
    BEGIN { inarr=0; obj=0; count=0; emit=0 }
    /^[[:space:]]*\[/ { if (!inarr) inarr=1; next }
    /^[[:space:]]*"features"[[:space:]]*:/ { inarr=1; next }
    inarr && obj==0 && /^[[:space:]]*{[[:space:]]*$/ {
      count++
      if (count==want) { emit=1; obj=1; print; next }
    }
    emit {
      print
      for (i=1; i<=length($0); i++) {
        c=substr($0,i,1); if (c=="{") obj++; if (c=="}") obj--
      }
      if (obj==0) exit
    }
  ' "$file" > "$out"
}

feature_file() {
  file="$1"; idx="$2"; out="$TMP_ROOT/feature_$idx.json"
  extract_feature "$file" "$((idx + 1))" "$out"
  printf '%s\n' "$out"
}

feature_has() {
  file="$1"; idx="$2"; key="$3"
  if [ "$HAS_JQ" -eq 1 ]; then
    jq -e --argjson i "$idx" --arg k "$key" "$JQ_FEATURE | has(\$k)" "$file" >/dev/null 2>&1
    return $?
  fi
  ff="$(feature_file "$file" "$idx")"
  grep -q '^[[:space:]]*"'$key'"[[:space:]]*:' "$ff"
}

feature_value() {
  file="$1"; idx="$2"; key="$3"
  if [ "$HAS_JQ" -eq 1 ]; then
    jq -r --argjson i "$idx" --arg k "$key" "$JQ_FEATURE | .[\$k] // empty" "$file"
    return
  fi
  ff="$(feature_file "$file" "$idx")"
  sed -n 's/^[[:space:]]*"'$key'"[[:space:]]*:[[:space:]]*"\(.*\)"[[:space:]]*,[[:space:]]*$/\1/p; s/^[[:space:]]*"'$key'"[[:space:]]*:[[:space:]]*\([^,]*\),[[:space:]]*$/\1/p; s/^[[:space:]]*"'$key'"[[:space:]]*:[[:space:]]*\([^,]*\)[[:space:]]*$/\1/p' "$ff" | sed 's/[[:space:]]*$//' | head -1
}

feature_type() {
  file="$1"; idx="$2"; key="$3"
  if [ "$HAS_JQ" -eq 1 ]; then
    jq -r --argjson i "$idx" --arg k "$key" "$JQ_FEATURE | .[\$k] | type" "$file"
    return
  fi
  ff="$(feature_file "$file" "$idx")"
  if grep -q '^[[:space:]]*"'$key'"[[:space:]]*:[[:space:]]*\[' "$ff"; then printf 'array\n'
  elif grep -q '^[[:space:]]*"'$key'"[[:space:]]*:[[:space:]]*\(true\|false\)' "$ff"; then printf 'boolean\n'
  elif grep -q '^[[:space:]]*"'$key'"[[:space:]]*:[[:space:]]*null' "$ff"; then printf 'null\n'
  elif grep -q '^[[:space:]]*"'$key'"[[:space:]]*:[[:space:]]*"' "$ff"; then printf 'string\n'
  else printf 'unknown\n'; fi
}

array_items() {
  file="$1"; idx="$2"; key="$3"
  if [ "$HAS_JQ" -eq 1 ]; then
    jq -r --argjson i "$idx" --arg k "$key" "$JQ_FEATURE | if (.[\$k]|type)==\"array\" then .[\$k][] else empty end" "$file"
    return
  fi
  ff="$(feature_file "$file" "$idx")"
  awk -v key="$key" '
    $0 ~ "^[[:space:]]*\"" key "\"[[:space:]]*:" {
      if ($0 ~ /\[[[:space:]]*\]/) exit
      if ($0 ~ /\[/) inarr=1
      next
    }
    inarr {
      if ($0 ~ /^[[:space:]]*\]/) exit
      print
    }
  ' "$ff" |
  sed -n 's/^[[:space:]]*"\(.*\)"[[:space:]]*,[[:space:]]*$/\1/p; s/^[[:space:]]*"\(.*\)"[[:space:]]*$/\1/p; s/^[[:space:]]*\([0-9][0-9]*\)[[:space:]]*,[[:space:]]*$/\1/p; s/^[[:space:]]*\([0-9][0-9]*\)[[:space:]]*$/\1/p'
}

array_length() {
  file="$1"; idx="$2"; key="$3"
  if [ "$HAS_JQ" -eq 1 ]; then
    jq -r --argjson i "$idx" --arg k "$key" "$JQ_FEATURE | if (.[\$k]|type)==\"array\" then (.[\$k]|length) else -1 end" "$file"
  else
    array_items "$file" "$idx" "$key" | awk 'END { print NR }'
  fi
}

ids_file_for() {
  file="$1"; count="$2"; out="$3"
  : > "$out"; i=0
  while [ "$i" -lt "$count" ]; do
    feature_value "$file" "$i" "id" >> "$out"
    i=$((i + 1))
  done
}

check_project() {
  project_dir="$1"
  file="$project_dir/feature_list.json"
  safe="$(printf '%s\n' "$project_dir" | tr '/ ' '__')"
  crit="$TMP_ROOT/critical_$safe.txt"; rec="$TMP_ROOT/recommended_$safe.txt"; ids="$TMP_ROOT/ids_$safe.txt"
  : > "$crit"; : > "$rec"
  FOUND_FEATURE_LIST=1; PROJECTS_TOTAL=$((PROJECTS_TOTAL + 1))

  printf '\n== %s ==\n' "$project_dir"
  if [ ! -f "$file" ]; then
    add_critical "-" "-" "feature_list.json no existe" "$crit"
    print_findings "CRITICAL" "$crit" "$RED" "[X]"
    print_findings "RECOMMENDED" "$rec" "$YELLOW" "[!]"
    return
  fi
  if ! json_valid "$file"; then
    add_critical "-" "-" "feature_list.json no es JSON valido/parseable" "$crit"
    print_findings "CRITICAL" "$crit" "$RED" "[X]"
    print_findings "RECOMMENDED" "$rec" "$YELLOW" "[!]"
    return
  fi

  count="$(feature_count "$file")"
  if [ "$count" -eq 0 ]; then
    add_critical "-" "-" "feature_list.json no contiene array de features auditable" "$crit"
  fi
  ids_file_for "$file" "$count" "$ids"

  base_project="$(basename "$project_dir")"
  if [ ! -f "$ROOT_DIR/projects/$base_project/CLAUDE.md" ]; then
    add_recommended "-" "-" "no existe projects/$base_project/CLAUDE.md correspondiente" "$rec"
  fi

  i=0
  while [ "$i" -lt "$count" ]; do
    fid="$(feature_value "$file" "$i" "id")"; fname="$(feature_value "$file" "$i" "name")"
    [ -n "$fid" ] || fid="index-$i"; [ -n "$fname" ] || fname="-"
    before_crit="$(wc -l < "$crit" | tr -d ' ')"; before_rec="$(wc -l < "$rec" | tr -d ' ')"

    for field in id name title description acceptance sdd design_doc boundary depends_on review_budget status; do
      feature_has "$file" "$i" "$field" || add_critical "$fid" "$fname" "falta campo obligatorio '$field'" "$crit"
    done
    [ "$(feature_type "$file" "$i" "acceptance")" = "array" ] || add_critical "$fid" "$fname" "acceptance debe ser array" "$crit"
    [ "$(feature_type "$file" "$i" "boundary")" = "array" ] || add_critical "$fid" "$fname" "boundary debe ser array" "$crit"
    [ "$(feature_type "$file" "$i" "depends_on")" = "array" ] || add_critical "$fid" "$fname" "depends_on debe ser array" "$crit"
    [ "$(feature_type "$file" "$i" "sdd")" = "boolean" ] || add_critical "$fid" "$fname" "sdd debe ser boolean" "$crit"

    status_value="$(feature_value "$file" "$i" "status")"
    case "$status_value" in
      pending|in_progress|spec_ready|done) ;;
      *) add_critical "$fid" "$fname" "status invalido '$status_value' (permitidos: pending, in_progress, spec_ready, done)" "$crit" ;;
    esac

    sdd_value="$(feature_value "$file" "$i" "sdd")"
    boundary_len="$(array_length "$file" "$i" "boundary")"
    if [ "$sdd_value" = "true" ] && [ "$boundary_len" -le 0 ]; then
      add_critical "$fid" "$fname" "sdd=true requiere boundary no vacio" "$crit"
    fi

    acc_len="$(array_length "$file" "$i" "acceptance")"
    if [ "$acc_len" -gt 0 ]; then
      skip_acceptance=0
      if [ "$acc_len" -eq 1 ]; then
        only_item="$(array_items "$file" "$i" "acceptance" | head -1)"
        words="$(printf '%s\n' "$only_item" | awk '{ print NF }')"
        [ "$words" -lt 15 ] && skip_acceptance=1
      fi
      if [ "$skip_acceptance" -eq 0 ]; then
        bad_acc="$TMP_ROOT/bad_acc_$i"; rm -f "$bad_acc"
        array_items "$file" "$i" "acceptance" | while IFS= read -r item; do
          printf '%s\n' "$item" | grep -Eq '^R[0-9]+:' || printf 'bad\n' > "$bad_acc"
        done
        if [ -f "$bad_acc" ]; then
          rm -f "$bad_acc"
          add_critical "$fid" "$fname" "acceptance no trivial debe usar prefijo R<n>: en cada string" "$crit"
        fi
      fi
    fi

    missing_dep="$TMP_ROOT/missing_dep_$i"; rm -f "$missing_dep"
    array_items "$file" "$i" "depends_on" | while IFS= read -r dep; do
      [ -n "$dep" ] || continue
      grep -qx "$dep" "$ids" || printf '%s\n' "$dep" >> "$missing_dep"
    done
    if [ -f "$missing_dep" ]; then
      deps="$(tr '\n' ' ' < "$missing_dep" | sed 's/[[:space:]]*$//')"
      rm -f "$missing_dep"
      add_critical "$fid" "$fname" "depends_on referencia ids inexistentes: $deps" "$crit"
    fi

    if [ "$status_value" = "done" ]; then
      ledger="$project_dir/progress/$fname/LEDGER.md"
      if [ ! -f "$ledger" ]; then
        add_recommended "$fid" "$fname" "status=done pero no existe progress/$fname/LEDGER.md" "$rec"
      elif ! grep -Eq 'task [0-9]+: .*status: done' "$ledger"; then
        add_recommended "$fid" "$fname" "LEDGER.md no contiene linea 'task N: ... status: done'" "$rec"
      fi
    fi
    if [ "$sdd_value" = "true" ] && [ ! -f "$project_dir/progress/$fname/design.md" ]; then
      add_recommended "$fid" "$fname" "sdd=true pero no existe progress/$fname/design.md" "$rec"
    fi

    after_crit="$(wc -l < "$crit" | tr -d ' ')"; after_rec="$(wc -l < "$rec" | tr -d ' ')"
    if [ "$after_crit" -eq "$before_crit" ] && [ "$after_rec" -eq "$before_rec" ]; then
      FEATURES_OK=$((FEATURES_OK + 1))
    else
      FEATURES_PROBLEMS=$((FEATURES_PROBLEMS + 1))
    fi
    i=$((i + 1))
  done

  print_findings "CRITICAL" "$crit" "$RED" "[X]"
  print_findings "RECOMMENDED" "$rec" "$YELLOW" "[!]"
}

if [ "$#" -gt 1 ]; then
  printf 'Uso: %s [path-al-proyecto]\n' "$0" >&2
  exit 2
fi

if [ "$#" -eq 1 ]; then
  check_project "$1"
else
  for base in "$ROOT_DIR/src" "$ROOT_DIR/projects"; do
    [ -d "$base" ] || continue
    for project_dir in "$base"/*; do
      [ -d "$project_dir" ] || continue
      [ -f "$project_dir/feature_list.json" ] || continue
      check_project "$project_dir"
    done
  done
fi

if [ "$FOUND_FEATURE_LIST" -eq 0 ]; then
  printf '[OK] no se encontro ningun feature_list.json en src/*/ ni projects/*/\n'
  exit 0
fi

printf '\n== Resumen global ==\n'
printf 'proyectos auditados: %s\n' "$PROJECTS_TOTAL"
printf 'features OK: %s\n' "$FEATURES_OK"
printf 'features con problemas: %s\n' "$FEATURES_PROBLEMS"

[ "$GLOBAL_CRITICAL" -eq 0 ] || exit 1
exit 0
