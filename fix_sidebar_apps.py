#!/usr/bin/env python3
"""
Script to fix 'apps:' namespace references in sidebar.html template
"""

import re


def fix_sidebar_template():
    file_path = r"C:\Users\rijas\Downloads\Projet\ATT\taxcollector\templates\velzon\partials\sidebar.html"

    # Read the file
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Pattern to match {% url 'apps:...' %} references
    pattern = r'<a href="{% url \'apps:[^\']*\'[^}]*%}"([^>]*)>'

    # Replace function
    def replace_apps_url(match):
        attributes = match.group(1)
        # Comment out the original and replace with placeholder
        original_line = match.group(0)
        commented_original = f"<!-- {original_line} -->"
        placeholder = f'<a href="#"{attributes}>'
        return f"{commented_original}\n                                    {placeholder}"

    # Apply the replacement
    fixed_content = re.sub(pattern, replace_apps_url, content)

    #
