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
                pvcreate /dev/vdb;
                vgcreate vg01 /dev/vdb;
                lvcreate -L 800M -n lv01 vg01;
                mkfs.xfs /dev/vg01/lv01;
                mkdir /mnt/data;
                mount /dev/vg01/lv01 /mnt/data;
                echo '/dev/vg01/lv01 /mnt/data xfs defaults 0 0' | sudo  tee -a /etc/fstab;
                yes | lvreduce -L 500M /dev/vg01/lv01
                echo '/usr/bin/cp /etc/fstab /tmp/fstab-capture.out' >> /etc/rc.d/rc.local
                echo '/usr/bin/cp /proc/self/mounts /tmp/mounts-capture.out' >> /etc/rc.d/rc.local
                ''',
                shell=True,
            ),
        ]
        userinterface.Console(items).run_items(action="Starting")

    def grade(self):
        items = []
        ui = userinterface.Console(items)
        ui.run_items(action="Grading")
        ui.report_grade()

    def finish(self):
        items = []
        userinterface.Console(items).run_items(action="Finishing")
