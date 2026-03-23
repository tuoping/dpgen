import os

from dpdata import LabeledSystem
from monty.serialization import dumpfn
import numpy as np

import dpgen.auto_test.lib.vasp as vasp
from dpgen import dlog
from dpgen.auto_test.Task import Task
from dpgen.generator.lib.vasp import incar_upper
from dpgen.util import sepline


class CP2K(Task):
    def __init__(self, inter_parameter, path_to_poscar):
        self.inter = inter_parameter
        self.inter_type = inter_parameter["type"]
        self.path_to_poscar = path_to_poscar

    def compute(self, output_dir):
        outcar = os.path.join(output_dir, "output")
        if not os.path.isfile(outcar):
            dlog.warning("cannot find " + outcar + " skip")
            return None
        else:
            ls = LabeledSystem(outcar, fmt="cp2k/output")
            stress = []
            for v in ls['virials']:
                assert v.shape == (3,3)
                stress.append([])
                for vx in v:
                    stress[-1].append(list(vx))
            # with open(outcar) as fin:
            #     lines = fin.read().split("\n")
            # for line in lines:
            #     if "in kB" in line:
            #         stress_xx = float(line.split()[2])
            #         stress_yy = float(line.split()[3])
            #         stress_zz = float(line.split()[4])
            #         stress_xy = float(line.split()[5])
            #         stress_yz = float(line.split()[6])
            #         stress_zx = float(line.split()[7])
            #         stress.append([])
            #         stress[-1].append([stress_xx, stress_xy, stress_zx])
            #         stress[-1].append([stress_xy, stress_yy, stress_yz])
            #         stress[-1].append([stress_zx, stress_yz, stress_zz])
            # 
            outcar_dict = ls.as_dict()
            outcar_dict["data"]["stress"] = {
                "@module": "numpy",
                "@class": "array",
                "dtype": "float64",
                "data": stress
            }

            return outcar_dict


    def make_potential_files(self, output_dir):
        dumpfn(self.inter, os.path.join(output_dir, "inter.json"), indent=4)

    def make_input_file(self, output_dir, task_type, task_param):
        pass


    def forward_files(self, property_type="relaxation"):
        return ["POSCAR"]

    def forward_common_files(self, property_type="relaxation"):
        potcar_not_link_list = ["vacancy", "interstitial"]
        if property_type == "elastic":
            return []
        elif property_type in potcar_not_link_list:
            return []
        else:
            return []

    def backward_files(self, property_type="relaxation"):
        return ["output"]
