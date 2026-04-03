import os
import json
from pathlib import Path

def get_title_from_markdown(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('# '):
                    return line[2:].strip()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return "未找到标题"

def generate_config(article_dir):
    index_md = article_dir / 'index.md'
    config_json = article_dir / 'config.json'
    
    if not index_md.exists():
        return
    
    title = get_title_from_markdown(index_md)
    
    # 判断分类
    category_id = "6809637769959178254"  # 默认后端
    dir_name = article_dir.name
    parent_dir = article_dir.parent.name
    
    # 前端相关
    frontend_keywords = ['vue', 'react', 'css', 'javascript', 'typescript', 'vite', 'webpack', 'web', 'frontend']
    if any(keyword in dir_name.lower() for keyword in frontend_keywords):
        category_id = "6809637767543259144"  # 前端
    
    # 职场相关
    if 'workplace' in dir_name.lower():
        category_id = "6809637776263217160"  # 代码人生
    
    # AI 相关
    if 'ai' in dir_name.lower() or 'llm' in dir_name.lower():
        category_id = "6809637773935378440"  # 人工智能
    
    config = {
        "categoryId": category_id,
        "tagIds": "6809640445233070094,6809640398105870343",
        "publish": True,
        "themeIds": "7243698841848348730",
        "title": title,
        "brief": "从原理到实战，掌握核心特性与最佳实践，阅读即可上手实践。"
    }
    
    with open(config_json, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
    
    print(f"Generated: {config_json}")

def main():
    base_dir = Path('databae')
    dates = ['0420', '0421', '0422', '0423', '0424', '0425', '0426']
    
    for date in dates:
        date_dir = base_dir / date
        if not date_dir.exists():
            continue
        
        for article_dir in date_dir.iterdir():
            if article_dir.is_dir():
                generate_config(article_dir)
    
    print("Done!")

if __name__ == '__main__':
    main()
