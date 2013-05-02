#!/usr/bin/env python

from __future__ import print_function
import sys
sys.path.append("..")
from cig_codes import code_db
import os
import subprocess

def main():
    if len(sys.argv) != 3:
        print("syntax:", sys.argv[0], "code_name|all release|dev")
        exit(1)

    req_name = sys.argv[1]
    code_type = sys.argv[2]
    if code_type != "release" and code_type != "dev":
        print("Unknown type (must be release or dev)")
        exit(1)

    for code_name in code_db.codes():
        if req_name != "all" and req_name != code_name: continue
        cmd_dict = {}
        cmd_dict["queue_cmd"] = "../queue/queue_daemon.sh doxygen_queue"
        cmd_dict["code_name"] = code_name
        if code_type == "release" and code_db.code_doxygen_release(code_name):
            cmd_dict["code_url"] = code_db.release_src[code_name]
            cmd_dict["code_version"] = code_db.release_version[code_name]
            sys_cmd = "{queue_cmd} \"cd `pwd` ; ./generate_doxygen.sh url {code_url} {code_version} {code_name}\" &".format(**cmd_dict)
            os.system(sys_cmd)
        elif code_type == "dev" and code_db.code_doxygen_dev(code_name):
            cmd_dict["repo_url"] = code_db.repo_url[code_name]
            cmd_dict["repo_type"] = code_db.repo_type[code_name]
            # Determine the latest revision number of the repository
            if code_db.repo_type[code_name] == "svn":
                svn_info = subprocess.check_output("svn info {repo_url}".format(**cmd_dict).split())
                rev_ind = svn_info.find("Last Changed Rev: ")+len("Last Changed Rev: ")
                cmd_dict["repo_version"] = svn_info[rev_ind:].split()[0]
            elif code_db.repo_type[code_name] == "hg":
                cmd_dict["repo_version"] = subprocess.check_output("hg id {repo_url}".format(**cmd_dict).split()).split()[0]
            elif code_db.repo_type[code_name] == "git":
                cmd_dict["repo_version"] = subprocess.check_output("git ls-remote {repo_url}".format(**cmd_dict).split()).split()[0]
            else:
                print("Unknown repository type for", code_name, "(must be svn, hg or git)")
                exit(1)
            sys_cmd = "{queue_cmd} \"cd `pwd` ; ./generate_doxygen.sh {repo_type} {repo_url} {repo_version} {code_name}\" &".format(**cmd_dict)
            os.system(sys_cmd)

if __name__ == "__main__":
    main()
