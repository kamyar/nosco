 # -*- coding: utf-8 -*-


"""nosco v0.5 - semantic version manager
  nōscō(/ˈnoːs.koː/ - in possession of knowledge)

       Semantic Version(http://semver.org)
   Manager Aims to provide a simple interface for
   determining the build version of software
   using rules privided in nosco.yaml

 Author: Kamyar Ghasemlou<kamyar@kamy.me>
"""
import os
from subprocess import check_output, Popen

import string

# in order to preserve the yaml structure
from .ordered_yaml import ordered_load, ordered_dump
from .ordered_yaml import OrderedDict

import pprint

# Used to extract keys used in a format string
formatter = string.Formatter()

class MercurialInfo(object):
    def __init__(self, project, module_args):
        self.project = project
        self.module_args = module_args
        # prioritize the module info to project info
        self.path = module_args['repo'] if 'repo' in module_args.keys() else project['path']
        # if no prefix is provided, then no prefix
        self.prefix = module_args.get('prefix', '')
        self.delimeter = module_args.get('branch_delimeter', '')
        self.hash_length = module_args.get('hash_length', 4)
        # print(prefix)

        self.hash_key = self.prefix+'hash'
        self.desc_key = self.prefix+'desc'
        self.branch_key = self.prefix+'branch'
        self.branch_cat = self.prefix+'branch_cat'
        self.major_key = self.prefix+'major'

        self.hg_command = ['hg', '-R', self.path, "parents", "--template"]
        self.hg_tag_command = ['hg', '-R', self.path, "tag"]

        # self.generate_keys()

    def generate_keys(self):
        res = {}
        res[self.hash_key] = check_output(self.hg_command+["{node}"])[:self.hash_length]
        res[self.desc_key] = check_output(self.hg_command+["{desc|firstline}"])
        res[self.branch_key] = check_output(self.hg_command+["{branch}"])
        # print branch_key, "|", res[branch_key]
        if(self.delimeter):
            try:
                res[self.branch_cat], res[self.major_key] = res[self.branch_key].split("/")
                res[self.major_key] = int(res[self.major_key])
            except IndexError as e:
                print("Branch name is not formatted correctly")
        else:
            res[self.major_key] = res[self.branch_key]
            res[self.branch_cat] = res[self.branch_key]

        if(res[self.desc_key].startswith(self.project["minor_bump_keyword"])):
            res["minor_bump"] = True;
        else:
            res["minor_bump"] = False;
        # print res
        return res

    def post_generate(self, generated_ver):
        # print self.module_args.get("tag", False)
        if self.module_args.get("tag", False):
            self.tag_repo(generated_ver)

    def tag_repo(self, tag):
        try:
            Popen(self.hg_tag_command+[tag])
            return 0
        except:
            return -1


nosco_modules = {'mercurial': MercurialInfo}


def key_in_dict(d, k):
    try:
        if k in d.keys():
            return True
        else:
            return False
    except:
        return False

class Nosco():
    """
        Nosco class provides the version info generation,
        formatting and config file handling
    """
    def __init__(self, conf_dir="", conf_name="nosco.yaml"):
        self.conf_dir = conf_dir
        self.conf_name = conf_name
        self.conf_path = os.path.join(conf_dir, conf_name)
        self.read_conf();
        self._generated_dict = {}

        self.generator_modules = []


    @property
    def project(self):
        return self.conf["project"]


    @property
    def history(self):
        return self.project["history"]

    def read_conf(self):
        "Read and Load Nosco config file as yaml."

        self.conf_fo = open(self.conf_path, 'r+');
        self.conf = ordered_load(self.conf_fo.read())

    def check_duplication(self, new_entry):
        "Check given new entry for duplication in conf history"


        new_major = new_entry['major']
        new_minor = new_entry['minor']
        new_patch = new_entry['patch']
        del new_entry['major']
        del new_entry['minor']
        del new_entry['patch']

        try:
            majors = list(self.history.keys())
        except:
            return 6    # No Majors


        if not key_in_dict(self.history, new_major):
            return 5    # Major does not exist

        if not key_in_dict(self.history[new_major], new_minor):
            return 4    # minor does not exist

        if not key_in_dict(self.history[new_major][new_minor], new_patch):
            return 3    # patch does not exist


        old_entry = dict(self.history[new_major][new_minor][new_patch])



        if new_entry != old_entry:
            return 2    # the entry is not equal
        else:
            return 0    # entry is equal





    def addNewEntry(self, new_entry, read_only):
        "Add a new entry to the history section and update the yaml file."

        new_major = new_entry['major']
        new_minor = new_entry['minor']
        new_patch = new_entry['patch']

        dup_check = self.check_duplication(new_entry)
        if read_only:
            return dup_check
        if(dup_check == 0):
            return dup_check

        if(dup_check == 6):
            self.history = OrderedDict()
            dup_check -= 1

        if(dup_check == 5):
            self.history[new_major] = OrderedDict()
            dup_check -= 1

        if dup_check == 4:
            self.history[new_major][new_minor] = OrderedDict()
            dup_check -= 1

        if dup_check == 3:
            self.history[new_major][new_minor][new_patch] = new_entry
            dup_check -= 1

        # if dup_check == 2:
        #     self.history[new_major][new_minor] = {}

        # else:
        #     print("Duplication check returned unknow code, version is not appended")
        # print self.history
        self.conf_fo.seek(0)
        self.conf_fo.truncate()
        self.conf_fo.write(ordered_dump(self.conf, default_flow_style=False))
        return dup_check

    @property
    def generated_dict(self):
        # print(self._generated_dict)
        "Finds and fills the generated keys"
        if(self._generated_dict):
            return self._generated_dict

        for module in self.conf["project"]["generate"]:
            app = module["app"]
            if(app in nosco_modules):
                curr_module = nosco_modules[app](self.project, module)
                module_results = curr_module.generate_keys()
                self._generated_dict.update(module_results)
                self.generator_modules.append(curr_module)
            else:
                print("ERROR: Module '{missing_module}' generator is not defined"\
                        .format(missing_module=app))
        return self._generated_dict

    def get_used_keys(self):
        "Returns a list of used format keys"
        return [i[1] for i in formatter.parse(self.project['build_format'])]

    def find_last_minor(self, major):
        """
            Gets current minor, patch tuple
                if new branch then both are 0
        """
        # if(major not in self.history.keys()):
        if(not key_in_dict(self.history, major)):
            return 0, 0
        major_tree = self.history[major]

        if not major_tree:
            max_minor = 0
            max_patch = 0
        else:
            max_minor = max(major_tree.keys())
            max_patch = max(major_tree[max_minor].keys())
        return max_minor, max_patch


    def get_format_dict(self):
        # keys used for formatting
        used_keys = self.get_used_keys()
        # keys provided by the conf file
        static_dict = self.project

        res = {}

        HAS_MINOR_BUMPED = False

        res['minor'], res['patch'] = self.find_last_minor(self.generated_dict['major'])
        # if("minor" in used_keys):
            # print(self.generated_dict)
        if(self.generated_dict['minor_bump']):
            HAS_MINOR_BUMPED = True
            # res['minor'] += 1
            res['patch'] = 0

        for k in used_keys:
            if(k in self.generated_dict.keys()):
                res[k] = self.generated_dict[k]
            elif(k in static_dict.keys()):
                res[k] = static_dict[k]
            if(k not in res):
                print("ERROR: {missing_key} has not been declared or generated, please check your configuration...".format(missing_key=k))
        # only patch is changing(major exists, minor has not changed)

        dup_stat = self.check_duplication(res.copy())
        if dup_stat == 0:   # hashes are equal and repos have not changed
            return res


        if(HAS_MINOR_BUMPED):
            res['minor'] += 1

        # print self.check_duplication(res.copy())
        dc = self.check_duplication(res.copy())
        if( dc == 2 and not HAS_MINOR_BUMPED):
            # print "increase patch"
            res['patch'] += 1
        return res


    def get_version(self, read_only=True):
        # self.complement_keys()
        format_dict = self.get_format_dict()
        build_format = self.conf['project']['build_format']
        # if not read_only:
        update_history_result = self.addNewEntry(format_dict.copy(), read_only)
        if(not update_history_result and not read_only):
            print("ERROR: Entry Already Exists, commit your changes!")
            return 1
        version_string =  build_format.format(**format_dict);


        if not read_only:
            for gm in self.generator_modules:
                gm.post_generate(version_string)


        return version_string



