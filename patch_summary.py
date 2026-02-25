
import re
import pathlib

with open('/a0/usr/projects/x-manage/src/site_generator.py', 'r') as f:
    lines = f.readlines()

new_lines = []
in_loop = False
for line in lines:
    if 'md_content = fpath.read_text' in line or 'md_content = ' in line:
        new_lines.append(line)
        new_lines.append('            # --- INJECTED SUMMARY LOGIC ---
')
        new_lines.append('            display_summary = ""
')
        new_lines.append('            for m_line in md_content.split("\n"):
')
        new_lines.append('                c_line = m_line.strip()
')
        new_lines.append('                if c_line and not c_line.startswith("#") and not c_line.startswith(">") and not c_line.startswith("!") and not c_line.startswith("|") and not c_line.startswith("-"):
')
        new_lines.append('                    display_summary += c_line + " "
')
        new_lines.append('                    if len(display_summary) > 130:
')
        new_lines.append('                        break
')
        new_lines.append('            display_summary = display_summary.strip()
')
        new_lines.append('            if len(display_summary) > 120:
')
        new_lines.append('                display_summary = display_summary[:117] + "..."
')
        new_lines.append('            elif not display_summary:
')
        new_lines.append('                display_summary = "Read the full technical breakdown and implementation guide inside..."
')
        new_lines.append('            # ------------------------------
')
        continue

    # Remove old display_summary assignments if they exist on their own line to prevent overwriting
    if 'display_summary =' in line and 'INJECTED SUMMARY LOGIC' not in "".join(new_lines[-15:]):
        if 'for m_line' not in line: # crude check
            continue

    new_lines.append(line)

with open('/a0/usr/projects/x-manage/src/site_generator.py', 'w') as f:
    f.writelines(new_lines)
