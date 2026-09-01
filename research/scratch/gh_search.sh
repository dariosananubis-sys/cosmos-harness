#!/bin/bash
# usage: gh_search.sh "query" outfile
export GH_TOKEN=$(security find-internet-password -s github.com -w)
Q="$1"
OUT="$2"
curl -s -H "Authorization: Bearer $GH_TOKEN" -G "https://api.github.com/search/repositories" \
  --data-urlencode "q=$Q" \
  --data-urlencode "sort=stars" \
  --data-urlencode "order=desc" \
  --data-urlencode "per_page=15" \
  | jq -r '.items[] | "\(.full_name) | ★\(.stargazers_count) | upd:\(.pushed_at[0:10]) | lic:\(.license.spdx_id // "none") | \(.description // "")"' > "$OUT"
echo "wrote $OUT ($(wc -l < "$OUT") lines)"
