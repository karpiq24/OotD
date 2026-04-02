import os
import sys
import yaml
import json

def get_prompts(content_dir):
    res = {}
    for root, dirs, files in os.walk(content_dir):
        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content.startswith('---'):
                            end = content.find('---', 3)
                            if end != -1:
                                fm = yaml.safe_load(content[3:end])
                                if isinstance(fm, dict) and 'image_prompt' in fm:
                                    res[file.replace('.md', '')] = fm['image_prompt']
                except Exception as e:
                    pass
    return res

if __name__ == "__main__":
    content_dir = sys.argv[1] if len(sys.argv) > 1 else "content"
    prompts = get_prompts(content_dir)
    print(json.dumps(prompts, indent=2, ensure_ascii=False))
