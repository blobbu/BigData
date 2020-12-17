import subprocess
process = subprocess.Popen(['sleep', '5'],
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
stdout, stderr = process.communicate()
print(stdout, stderr)
