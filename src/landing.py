from dotenv import dotenv_values
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from lxml import etree
import markdown
import os
import re
import shutil

env_vars = dotenv_values(".env")

def main():
    jinja2_env = Environment(loader=FileSystemLoader("src/templates"), autoescape=False)
    sitemap_src = etree.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    dist_path = "dist/landing"
    sitemap_exclude = ["404.md"]
    src_md_path = "src/markdown"
    src_static_path = "src/static_root"

    shutil.rmtree(dist_path, True)
    shutil.copytree(src_static_path, dist_path)

    for file in os.listdir(src_md_path):
        # Sitemap logic
        if file not in sitemap_exclude:
            url_element = etree.SubElement(sitemap_src, "url")
            slug = (
                file.replace("_", "/").replace(".md", "")
                if file != "index.md"
                else ""
            )
            etree.SubElement(url_element, "loc").text = f"{env_vars['SITE_URL']}/{slug}"

        # Template logic
        file_path = f"{src_md_path}/{file}"
        dist_file = file.replace(".md", ".html")
        dist_file_path = f"{dist_path}/{dist_file}"

        try:
            templates = jinja2_env.get_template(dist_file)
        except TemplateNotFound:
            templates = jinja2_env.get_template("default.html")

        with open(file_path, "r") as f:
            jinja2_html = templates.render(
                content=markdown.markdown(
                    f.read(),
                    extensions=["tables", "fenced_code", "codehilite", "toc"],
                ),
                **{key: value for key, value in re.findall(r"<!--\s*(.*?):\s*(.*?)\s*-->", f.read())},
                **env_vars,
                slug=slug,
            )

        with open(dist_file_path, "w") as f:
            f.write(jinja2_html)

    with open(f"{dist_path}/sitemap.xml", "w") as file:
        file.write(etree.tostring(sitemap_src).decode("utf8"))

main()
