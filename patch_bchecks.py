import os
import glob
import re

def process_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Skip files that are already patched or are SQLi (which we did manually)
    if 'status_code} is "400"' in content or 'sqli-' in filepath:
        return False
        
    # Find the variable name used for response
    # Usually it's {latest.response} or {check.response}
    var_match = re.search(r'\{(latest|check|base|\w+Payload|\w+Check)\.response', content)
    if not var_match:
        # Fallback to check if it's just not there
        return False
        
    var_name = var_match.group(1)

    # We want to replace the first `if` statement after `send payload:` or `send request:`
    # with an if not({var_name}.response.status_code is "400") then block wrapping ALL subsequent code until the end of the `given` block.
    # Actually, BChecks end with the file. So we can just find the first `if ` in the `given` block
    # and wrap everything from there to the end.
    
    # Let's find the first `if ` after `given `
    lines = content.split('\n')
    new_lines = []
    
    in_given = False
    in_if = False
    found_first_if = False
    
    for line in lines:
        if line.startswith('given '):
            in_given = True
            
        if in_given and line.strip().startswith('if ') and not found_first_if:
            # We found the first if block
            # Determine the indentation
            indent = len(line) - len(line.lstrip())
            indent_str = ' ' * indent
            new_lines.append(f'{indent_str}if not({{{var_name}.response.status_code}} is "400") then')
            # Indent this line and all subsequent lines until the end
            new_lines.append('    ' + line)
            found_first_if = True
        elif found_first_if:
            # Indent subsequent lines by 4 spaces
            if line.strip() == '':
                new_lines.append(line)
            else:
                new_lines.append('    ' + line)
        else:
            new_lines.append(line)
            
    if found_first_if:
        # Close the wrapper if
        new_lines.append(' ' * indent + 'end if')
        
    with open(filepath, 'w') as f:
        f.write('\n'.join(new_lines))
        
    return found_first_if

files_to_patch = [
    'cmdi-blind-time-based.bcheck',
    'cmdi-multi-vector-waf-bypass.bcheck',
    'xss-csp-bypass-vectors.bcheck',
    'xss-dangling-markup-injection.bcheck',
    'xss-dom-based-sink-detection.bcheck',
    'xss-reflected-waf-bypass.bcheck',
    'xss-stored-via-headers.bcheck',
    'xxe-blind-oob-exfiltration.bcheck',
    'xxe-classic-file-read-waf-bypass.bcheck',
    'ssrf-blind-oob-detection.bcheck',
    'ssrf-cloud-metadata-waf-bypass.bcheck',
    'ssrf-internal-network-probing.bcheck',
    'path-traversal-multi-os-waf-bypass.bcheck',
    'deserialization-multi-language-active.bcheck',
    'deserialization-multi-language-passive.bcheck',
    'file-upload-extension-bypass.bcheck',
    'host-header-injection-reset-poisoning.bcheck',
    'prototype-pollution-client-server.bcheck',
    'dom-clobbering-detection.bcheck',
    'dom-open-redirect.bcheck'
]

for f in files_to_patch:
    if os.path.exists(f):
        if process_file(f):
            print(f"Patched {f}")
        else:
            print(f"Skipped {f}")
    else:
        print(f"Not found {f}")
