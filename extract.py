import os, shutil, re

html = open('e:/_WORK_/form-n-space/website/formnspaceimphal.com/category/projects/projects.html', encoding='utf-8', errors='ignore').read()
articles = re.findall(r'<article[^>]*>(.*?)</article>', html, re.DOTALL)

dest_dir = 'e:/_WORK_/form-n-space/website/app/src/assets/projects-thumb'
os.makedirs(dest_dir, exist_ok=True)

src_base = 'e:/_WORK_/form-n-space/website/formnspaceimphal.com/category/projects/'

count = 0
for art in articles:
    img_m = re.search(r'src="([^"]+\.(?:jpg|png|jpeg|webp))"', art)
    if not img_m:
        continue
    rel = img_m.group(1)  # e.g. ../../wp-content/uploads/...
    abs_src = os.path.normpath(os.path.join(src_base, rel))
    fname = os.path.basename(abs_src)
    dst = os.path.join(dest_dir, fname)
    if os.path.exists(abs_src):
        shutil.copy2(abs_src, dst)
        print(f'OK: {fname}')
        count += 1
    else:
        print(f'MISSING: {abs_src}')

print(f'\nCopied {count} thumbnails')
