"""set en of one row: setrow.py ID 'english with \\n'"""
import json, sys, pathlib
sys.path.insert(0, 'H:/translation/eithea/tools')
import text
i, en = sys.argv[1], sys.argv[2].replace('\\n', '\n')
key = i.rsplit(':', 1)[0]
p = text.OUT / f'{key}.json'
rows = json.loads(p.read_text(encoding='utf-8'))
for r in rows:
    if r['id'] == i:
        r['en'] = en
        print(text.lint(r) or 'ok')
p.write_text(json.dumps(rows, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
