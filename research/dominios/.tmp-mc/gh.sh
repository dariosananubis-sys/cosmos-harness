#!/bin/bash
export GH_TOKEN=$(security find-internet-password -s github.com -w 2>/dev/null)
gh_search() {
  local q="$1"
  curl -s --max-time 15 -H "Authorization: Bearer $GH_TOKEN" -H "Accept: application/vnd.github+json" \
    "https://api.github.com/search/repositories?q=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$q")&sort=stars&order=desc&per_page=15" \
    | python3 -c "
import json,sys
d=json.load(sys.stdin)
if 'items' not in d:
    print('ERROR', d.get('message',d))
    sys.exit(0)
for r in d['items']:
    print(f\"{r['stargazers_count']:>6}★ {r['full_name']:<45} lic={ (r.get('license') or {}).get('spdx_id') } push={r['pushed_at'][:10]} | {(r['description'] or '')[:90]}\")
"
}
gh_repo() {
  local r="$1"
  curl -s --max-time 15 -H "Authorization: Bearer $GH_TOKEN" -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/$r" \
    | python3 -c "
import json,sys
d=json.load(sys.stdin)
if 'full_name' not in d:
    print('ERROR', d.get('message',d))
    sys.exit(0)
print(f\"{d['full_name']} | {d['stargazers_count']}★ | lic={(d.get('license') or {}).get('spdx_id')} | pushed={d['pushed_at'][:10]} | archived={d.get('archived')} | fork={d.get('fork')}\")
print(f\"desc: {d.get('description')}\")
"
}
