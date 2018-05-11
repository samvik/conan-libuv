import subprocess
import re
import sys
import platform

def find_python(desired_version):
    python_executables = [sys.executable]
    if platform.system() == "Windows":
        python_executables.extend(["python.exe", "python2.exe", "python3.exe"])
    else:
        python_executables.extend(["python", "python2", "python3"])
    
    regex = re.compile(r'.*(\d+\.\d+\.\d+).*', re.IGNORECASE)
    
    for exe in python_executables:
        output = subprocess.check_output([exe, "-V"], stderr=subprocess.STDOUT).decode("utf-8")
        if output:
            result = regex.match(output);
            version = result.group(1)
            if version.startswith(desired_version):
                return exe
            
    return ""
    
