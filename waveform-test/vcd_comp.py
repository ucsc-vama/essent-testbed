import collections
import sys

#first argument must be verilator vcd and second argument is ESSENT VCD
vcdFile1 = sys.argv[1]
vcdFile2 = sys.argv[2]
is_ver1 = sys.argv[3]
is_ver2 = sys.argv[4]

with open(vcdFile1,'r') as f1, open(vcdFile2,'r') as f2:
    vcd1 = f1.readlines()
    vcd2 = f2.readlines()

vcd1_header = []
vcd2_header = []

for line in vcd1:
    if "$enddefinitions $end" in line:
        break
    else:
        vcd1_header.append(line)

for line2 in vcd2:
    if "$enddefinitions $end" in line2:
        break
    else:
        vcd2_header.append(line2)

vcd1_mod = []
vcd2_mod = []

#modules check
for i in vcd1_header:
    if "scope module" in i:
        mod_name = i[i.find("module ") + 7:i.find(" $end")]
        vcd1_mod.append(mod_name)

for i in vcd2_header:
    if "scope module" in i:
        mod_name = i[i.find("module ") + 7:i.find(" $end")]
        vcd2_mod.append(mod_name)

if is_ver1 == "True":
    print("First vcd is Verilator's VCD")
    vcd1_mod.remove("TOP")

if is_ver2 == "True":
    print("Second vcd is Verilator's VCD")
    vcd2_mod.remove("TOP")

if collections.Counter(vcd1_mod) == collections.Counter(vcd2_mod):
    print ("The modules are the same in both vcds") 
else: 
    print ("The modules are not the same in both vcds")
    print("Modules present in essent , not in verilator")
    extra_vcd2_mod = list(set(vcd2_mod) - set(vcd1_mod))
    print(extra_vcd2_mod)
    print("Modules present in verilator , not in essent")
    extra_vcd1_mod = list(set(vcd1_mod) - set(vcd2_mod))
    print(extra_vcd1_mod)

#store the signals whole name from the Tile or Top most module of vcd file 
# key - signal name , value - identifier code 
vcd1_signal = {}
temp_hier = []
for line in vcd1_header:
    if "scope module" in line:
        mod_name = line[line.find("module ") + 7:line.find(" $end")]
        temp_hier.append(mod_name)
        temp_hier.append("$")
    elif "upscope" in line:
        temp_hier.pop(-1)
        temp_hier.pop(-1)
    elif "wire" in line:
        if ("wire 128" in line) | ("wire 256" in line) | ("wired 512" in line):
            temp = line[line.find("wire") + 9:line.find("$end")]
        else :
            temp = line[line.find("wire") + 8:line.find("$end")]
        iden_code = temp[0:temp.find(" ")]
        temp1 = temp[temp.find(" ") + 1:]
        signal_name = temp1[:temp1.find(" ")]
        key = ''.join(map(str,temp_hier)) + signal_name
        if is_ver1 == "True":
            up_key = key.replace('TOP$','')
            key = up_key
        vcd1_signal[key] = iden_code

#print(vcd1_signal)

vcd2_signal = {}
temp_hier = []
for line in vcd2_header:
    if "scope module" in line:
        mod_name = line[line.find("module ") + 7:line.find(" $end")]
        temp_hier.append(mod_name)
        temp_hier.append("$")
    elif "upscope" in line:
        temp_hier.pop(-1)
        temp_hier.pop(-1)
    elif "wire" in line:
        if ("wire 128" in line) | ("wire 256" in line) | ("wired 512" in line):
            temp = line[line.find("wire") + 9:line.find("$end")]
        else :
            temp = line[line.find("wire") + 8:line.find("$end")]
        iden_code = temp[0:temp.find(" ")]
        temp1 = temp[temp.find(" ") + 1:]
        signal_name = temp1[:temp1.find(" ")]
        key = ''.join(map(str,temp_hier)) + signal_name
        if is_ver2 == "True":
            up_key = key.replace('TOP$','')
            key = up_key
        vcd2_signal[key] = iden_code

#print(vcd2_signal)

#compare between the signals between two vcd input files
diff_signals1_2 = set(vcd1_signal) - set(vcd2_signal)
print("Signals which are present in 1st input vcd, not present in 2nd input vcd")
print(diff_signals1_2)

diff_signals2_1 = set(vcd2_signal) - set(vcd1_signal)
print("Signals which are present in 2nd input vcd, not present in 1st input vcd")
print(diff_signals2_1)


start_cycle = 0
vcd1_signal_value = {}
for i in vcd1:
    if start_cycle == 1:
        if "b" in i:
            iden_code = i[i.find(" ") +1:-1]
            value = i[1:i.find(" ")]
            vcd1_signal_value[iden_code] = value
        else:
            iden_code = i[1:-1]
            value = i[0]
            vcd1_signal_value[iden_code] = value
    if i.startswith('#'):
        if start_cycle == 1:
            start_cycle = 0
            break
        else:
            start_cycle = 1
        cycle_count = i[1]

