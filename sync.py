import markdown2
import os
import re
import json
from datetime import datetime

def create_blog_post(md_file_path, template_path, output_dir):
    """
    Converts a single Markdown file to a styled HTML blog post.
    Returns the path to the created file if successful, otherwise None.
    """
    print(f"--- Processing: {md_file_path} ---")

    output_filename = os.path.splitext(os.path.basename(md_file_path))[0] + '.html'
    output_path = os.path.join(output_dir, output_filename)

    if os.path.exists(output_path):
        print(f"⏩ Skipping conversion: '{output_path}' already exists.")
        return output_path # Return existing path for index update

    try:
        with open(md_file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
    except FileNotFoundError:
        print(f"❌ Error: Markdown file not found at '{md_file_path}'")
        return None

    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_html = f.read()
    except FileNotFoundError:
        print(f"❌ Error: HTML template not found at '{template_path}'")
        return None

    title_match = re.search(r'^#\s+(.*)', md_content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "Untitled Post"

    html_content = markdown2.markdown(md_content, extras=['fenced-code-blocks', 'tables'])

    final_html = template_html.replace('<!-- BLOG_TITLE_PLACEHOLDER -->', title)
    final_html = final_html.replace('<!-- BLOG_CONTENT_PLACEHOLDER -->', html_content)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    print(f"✅ Success! Created: '{output_path}'")
    return output_path

def update_index_html(content_to_inject, placeholder, index_path='index.html'):
    """
    A generic function to inject HTML content into a placeholder in a file.
    """
    print(f"\n--- Updating '{placeholder}' in {index_path} ---")
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            index_content = f.read()
    except FileNotFoundError:
        print(f"❌ Error: Main page '{index_path}' not found.")
        return

    placeholder_start = f'<!-- {placeholder}_START -->'
    placeholder_end = f'<!-- {placeholder}_END -->'
    
    updated_content = re.sub(
        f'{placeholder_start}(.|\n)*?{placeholder_end}',
        f'{placeholder_start}\n{content_to_inject}\n                        {placeholder_end}',
        index_content
    )

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"✅ Success! {index_path} has been updated.")

def generate_projects_html(projects_json_path='projects.json'):
    print("\n--- Generating Projects HTML ---")
    try:
        with open(projects_json_path, 'r', encoding='utf-8') as f:
            projects = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: '{projects_json_path}' not found.")
        return ""
    except json.JSONDecodeError:
        print(f"❌ Error: Could not decode JSON from '{projects_json_path}'. Check for syntax errors.")
        return ""

    projects_html = ""
    for project in projects:
        tags_html = "".join([f'<span class="bg-gray-700 text-xs font-semibold px-2.5 py-1 rounded-full">{tag}</span>' for tag in project.get("tags", [])])
        
        live_demo_button = ""
        if project.get("liveDemoUrl"):
            live_demo_button = f"""<a href="{project['liveDemoUrl']}" target="_blank" class="text-[var(--neon-green)] hover:opacity-80 font-semibold flex items-center space-x-1"><i data-lucide="external-link" class="h-5 w-5"></i><span>Live Demo</span></a>"""

        projects_html += f"""
                        <div class="project-card glass-card rounded-2xl overflow-hidden group flex flex-col">
                            <img src="{project.get('image', 'https://placehold.co/600x300/1f2937/bfff00?text=Project')}" alt="{project.get('title', 'Project')}" class="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-500">
                            <div class="p-6 flex flex-col flex-grow">
                                <h3 class="text-xl font-bold text-white mb-2">{project.get('title', 'Untitled Project')}</h3>
                                <p class="text-gray-300 mb-4 flex-grow">{project.get('description', '')}</p>
                                <div class="flex flex-wrap gap-2 mb-4">{tags_html}</div>
                                <div class="flex items-center space-x-4 mt-auto">
                                    <a href="{project.get('sourceCodeUrl', '#')}" target="_blank" class="text-[var(--neon-green)] hover:opacity-80 font-semibold flex items-center space-x-1"><i data-lucide="github" class="h-5 w-5"></i><span>Source Code</span></a>
                                    {live_demo_button}
                                </div>
                            </div>
                        </div>"""
    print(f"✅ Generated HTML for {len(projects)} projects.")
    return projects_html

def generate_blog_html(blog_dir='blog'):
    print("\n--- Generating Blog Post List HTML ---")
    blog_posts = []
    for filename in os.listdir(blog_dir):
        if filename.endswith('.html'):
            html_file_path = os.path.join(blog_dir, filename)
            details = extract_post_details(html_file_path)
            if details:
                blog_posts.append(details)
    
    blog_posts.sort(key=lambda p: p['date_obj'], reverse=True)

    posts_html = ""
    for post in blog_posts:
        posts_html += f"""
                        <div class="blog-post-entry flex flex-col sm:flex-row items-center gap-8 py-4 border-b border-[var(--border-color-rgba)]">
                            <div class="flex-grow">
                                <p class="text-sm text-gray-400 mb-2">{post['date_str']}</p>
                                <h3 class="text-xl font-bold text-white mb-2">{post['title']}</h3>
                                <p class="text-gray-300 mb-4">{post['description']}...</p>
                            </div>
                            <a href="{post['path']}" class="flex-shrink-0 text-[var(--neon-green)] hover:opacity-80 font-semibold flex items-center space-x-1">
                                <span>Read More</span>
                                <i data-lucide="arrow-right" class="h-5 w-5"></i>
                            </a>
                        </div>"""
    print(f"✅ Generated HTML for {len(blog_posts)} blog posts.")
    return posts_html

def extract_post_details(html_path):
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        title_match = re.search(r'<title>(.*?) \| hxr3tic</title>', content)
        title = title_match.group(1) if title_match else "Untitled"
        
        desc_match = re.search(r'<div class="blog-content">.*?<p>(.*?)</p>', content, re.DOTALL)
        description = desc_match.group(1).strip() if desc_match else "Click to read more"
        description = re.sub('<[^<]+?>', '', description)
        if len(description) > 150:
            description = description[:150].strip()
        
        creation_time = os.path.getmtime(html_path)
        date_obj = datetime.fromtimestamp(creation_time)
        date_str = date_obj.strftime("%B %d, %Y")

        return {
            'title': title,
            'description': description,
            'path': f"blog/{os.path.basename(html_path)}",
            'date_obj': date_obj,
            'date_str': date_str
        }
    except Exception as e:
        print(f"⚠️ Could not extract details from {html_path}: {e}")
        return None

# --- MAIN EXECUTION ---
def main():
    """
    Main function to run the full blog generation and update process.
    """
    source_dir = 'blogs_md'
    output_dir = 'blog'
    template_file = 'template.html'
    projects_file = 'projects.json'
    index_file = 'index.html'

    # --- Step 1: Convert Markdown blog posts to HTML ---
    if os.path.isdir(source_dir):
        os.makedirs(output_dir, exist_ok=True)
        print("🚀 Starting blog build process...")
        for filename in os.listdir(source_dir):
            if filename.endswith('.md'):
                md_file_path = os.path.join(source_dir, filename)
                create_blog_post(md_file_path, template_file, output_dir)
    else:
        print(f"ℹ️  Note: Source directory '{source_dir}' not found. Skipping blog post creation.")

    # --- Step 2: Generate HTML for projects from JSON ---
    projects_html_content = generate_projects_html(projects_file)
    if projects_html_content:
        update_index_html(projects_html_content, 'PROJECTS_PLACEHOLDER', index_file)

    # --- Step 3: Generate HTML for blog list from converted files ---
    if os.path.isdir(output_dir):
        blog_html_content = generate_blog_html(output_dir)
        if blog_html_content:
            update_index_html(blog_html_content, 'BLOG_POSTS_PLACEHOLDER', index_file)
    
    print("\n🎉 All done!")


if __name__ == '__main__':
    main()
