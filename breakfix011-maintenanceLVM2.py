#
# Copyright (c) 2020 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.

from labs import labconfig
from labs.grading import Default
from labs.common import steps, labtools, userinterface

SKU = labconfig.get_course_sku().upper()

_targets = ["servera"]
_servera = "servera"

class Breakfix011Maintenancelvm2(Default):
    __LAB__ = "breakfix011-maintenanceLVM2"

    def start(self):
        items = [
            {
                "label": "Checking lab systems",
                "task": labtools.check_host_reachable,
                "hosts": _targets,
                "fatal": True,
            },
            steps.run_command(
                label="Configuring " + _servera,
                hosts=[_servera],
                command='''
                pvcreate -f /dev/vdb;
                vgcreate vg01 /dev/vdb;
                lvcreate -L 800M -n lv01 vg01;
                mkfs.xfs /dev/vg01/lv01;
                mkdir /mnt/data;
                mount /dev/vg01/lv01 /mnt/data;
                echo '/dev/vg01/lv01 /mnt/data xfs defaults 0 0' | sudo  tee -a /etc/fstab;
                yes | lvreduce -L 500M /dev/vg01/lv01;
                echo '/usr/bin/cp /etc/fstab /tmp/fstab-capture.out' >> /etc/rc.d/rc.local;
                echo '/usr/bin/cp /proc/self/mounts /tmp/mounts-capture.out' >> /etc/rc.d/rc.local;
                reboot;
                ''',
                shell=True,
            ),
        ]
        userinterface.Console(items).run_items(action="Starting")

    def grade(self):
        """
        Perform evaluation steps on the system
        """
        items = [
            {
                "label": "Checking lab systems",
                "task": labtools.check_host_reachable,
                "hosts": _targets,
                "fatal": True,
            },
            steps.run_command(
                label="Verifying lab system " + _servera,
                hosts=[_servera],
                command='''[ ! -z $(systemctl list-units --type target --state active | grep -o $(systemctl get-default)) ] 2>> /dev/null''',
                returns="0",
                shell=True,
            ),
            steps.run_command(
                label="Verifying lab system " + _servera,
                hosts=[_servera],
                command='''[[ ! -z $(pvscan 2>&1 | grep -o "PV /dev/vdb   VG vg01") ]] 2>> /dev/null''',
                returns="0",
                shell=True,
            ),
            steps.run_command(
                label="Verifying lab system " + _servera,
                hosts=[_servera],
                command='''[ ! -z "$(blkid|grep -o /dev/mapper/vg01-lv01)" ] 2>> /dev/null''',
                returns="0",
                shell=True,
            ),
            steps.run_command(
                label="Verifying lab system " + _servera,
                hosts=[_servera],
                command='''[ ! -z $(lvs 2>> /dev/null | awk '($2=="vg01"){print $3}' | grep -o a) ]''',
                returns="0",
                shell=True,
            ),
            steps.run_command(
                label="Verifying lab system " + _servera,
                hosts=[_servera],
                command='''[ ! -z "$(grep /dev/mapper/vg01-lv01 /proc/self/mounts|grep -o "/mnt/data")" ] &>> /dev/null''',
                returns="0",
                shell=True,
            ),
            steps.run_command(
                label="Verifying lab system " + _servera,
                hosts=[_servera],
                command='''[ -z "$(egrep "root|swap|app" /tmp/fstab-capture.out 2>&1|egrep -o "#|No")" ] &>> /dev/null''',
                returns="0",
                shell=True,
            ),
            steps.run_command(
                label="Verifying lab system " + _servera,
                hosts=[_servera],
                command='''[ ! -z "$(grep /dev/mapper/vg01-lv01 /tmp/mounts-capture.out 2>/dev/null|grep -o "/mnt/data")" ] &>> /dev/null''',
                returns="0",
                shell=True,
            ),
            steps.run_command(
                label="Verifying lab system " + _servera,
                hosts=[_servera],
                command='''[ -z "$(journalctl -xb | grep -o emergency | sort -u)" ] &>> /dev/null''',
                returns="0",
                shell=True,
            ),
        ]
        ui = userinterface.Console(items)
        ui.run_items(action="Grading")
        ui.report_grade()

    def finish(self):
        items = [
            {
                "label": "Checking lab systems",
                "task": labtools.check_host_reachable,
                "hosts": _targets,
                "fatal": True,
            },
            steps.run_command(
                label="Removing the settings from " + _servera,
                hosts=[_servera],
                command='''
                umount /mnt/data;
                rm -rf /mnt/data;
                lvremove -f /dev/vg01/lv01;
                vgremove vg01;
                pvremove /dev/vdb1;
                egrep -v -e '/dev/vg01/lv01 /mnt/data xfs defaults 0 0' /etc/fstab > /tmp/fstab && mv -f /tmp/fstab /etc/fstab;
                # fix;
                # mount -o remount,rw /
                # lvextend -L 1G /dev/mapper/application-app
                # mount -a
                # reboot
                ''',
                shell=True,
            ),
        ]
        userinterface.Console(items).run_items(action="Finishing")
