#!/usr/bin/python3

import os
import sys
import time


def message(msg):
    sys.stdout.write(msg + '\n')
    sys.stdout.flush()


def call(command):
    message("Running %s" % command)
    return os.system(command) == 0


def bundle(vmname, vmuser, sshadress):
    vm_home = "/home/%s" % vmuser
    vm_ssh = "%s@%s" % (vmuser, sshadress)
    ges_ci_folder = "%s/devel/ges-ci/" % vm_home

    call("VBoxManage startvm %s --type headless" % vmname)
    t = time.time()
    while not call("ssh %s echo 'Vm is up and running'" % (vm_ssh)):
        if time.time() - t > 600:
            message("TIMEOUT, could not connect to VM")
            # call("VBoxManage controlvm %s savestate" % vmname)
            return False

    if not call("ssh %s 'cd %s && git fetch origin && git reset --hard origin/master'"
                % (vm_ssh, ges_ci_folder)):
        message("Fetching update_bundle script failed")
        return False

    if not call("ssh %s '%s/devel/ges-ci/update_bundle latest'" % (vm_ssh, vm_home)):
        message("Update bundle FAILED")
        return False

    return True


if __name__ == "__main__":
    ret = 0

    vms = []

    if "32bits" in sys.argv:
        vms.append(("debian_wheezy_32", "gstqa", "192.168.1.92"))

    if "64bits" in sys.argv:
        vms.append(("debian_wheezy", "gst-qa", "192.168.1.99"))

    if not vms:
        vms.append(("debian_wheezy", "gst-qa", "192.168.1.99"))

    for vmname, vmuser, sshadress in vms:
        if not bundle(vmname, vmuser, sshadress):
            ret = 1
            message("ERROR, Could not create %s bundle" % (vmname))

    exit(ret)
