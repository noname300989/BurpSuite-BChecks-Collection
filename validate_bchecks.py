import os
import glob
import re

def validate_bcheck(file_path):
    errors = []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
        
    has_metadata = False
    has_given = False
    if_count = 0
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('metadata:'):
            has_metadata = True
        elif stripped.startswith('given '):
            has_given = True
        elif stripped.startswith('if ') and ' then' in stripped:
            if_count += 1
        elif stripped == 'end if':
            if_count -= 1
            if if_count < 0:
                errors.append(f"Line {i+1}: 'end if' without matching 'if'")
                if_count = 0 # reset to prevent cascade
                
    if if_count > 0:
        errors.append(f"Missing {if_count} 'end if' statement(s)")
        
    if not has_metadata:
        errors.append("Missing 'metadata:' block")
    if not has_given:
        errors.append("Missing 'given ... then' block")
        
    return errors

def main():
    bcheck_files = glob.glob('*.bcheck')
    if not bcheck_files:
        print("No .bcheck files found in current directory.")
        return
        
    total_files = len(bcheck_files)
    files_with_errors = 0
    
    for bcheck in bcheck_files:
        errors = validate_bcheck(bcheck)
        if errors:
            files_with_errors += 1
            print(f"[FAIL] {bcheck}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"[PASS] {bcheck}")
            
    print("-" * 30)
    print(f"Total files tested: {total_files}")
    if files_with_errors == 0:
        print("All files passed basic syntax validation!")
    else:
        print(f"{files_with_errors} files have syntax errors.")

if __name__ == '__main__':
    main()
