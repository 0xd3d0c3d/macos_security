#!/usr/bin/env python3
# filename: generate_guidance.py
# description: Process a given baseline, and output guidance files

import os.path
import glob
import os
import yaml
import argparse


class MacSecurityRule():
    def __init__(self, title, rule_id, severity, discussion, check, fix, cci, cce, nist_controls, disa_stig, srg, tags, result_value, mobileconfig, mobileconfig_info):
        self.rule_title = title
        self.rule_id = rule_id
        self.rule_severity = severity
        self.rule_discussion = discussion
        self.rule_check = check
        self.rule_fix = fix
        self.rule_cci = cci
        self.rule_cce = cce
        self.rule_80053r4 = nist_controls
        self.rule_disa_stig = disa_stig
        self.rule_srg = srg
        self.rule_result_value = result_value
        self.rule_tags = tags
        self.rule_mobileconfig = mobileconfig
        self.rule_mobileconfig_info = mobileconfig_info

    def create_asciidoc(self, adoc_rule_template):
        """Pass an AsciiDoc template as file object to return formatted AsciiDOC"""
        rule_adoc = ""
        rule_adoc = adoc_rule_template.substitute(
            rule_title=self.rule_title,
            rule_id=self.rule_id,
            rule_severity=self.rule_severity,
            rule_discussion=self.rule_discussion,
            rule_check=self.rule_check,
            rule_fix=self.rule_fix,
            rule_cci=self.rule_cci,
            rule_80053r4=self.rule_80053r4,
            rule_disa_stig=self.rule_disa_stig,
            rule_srg=self.rule_srg,
            rule_result=self.rule_result_value
        )
        return rule_adoc


def get_rule_yaml(rule_file):
    """ Takes a rule file, checks for a custom version, and returns the yaml for the rule
    """
    if os.path.basename(rule_file) in glob.glob1('../custom/rules/', '*.yaml'):
        #print(f"Custom settings found for rule: {rule_file}")
        override_rule = os.path.join(
            '../custom/rules', os.path.basename(rule_file))
        with open(override_rule) as r:
            rule_yaml = yaml.load(r, Loader=yaml.SafeLoader)
    else:
        with open(rule_file) as r:
            rule_yaml = yaml.load(r, Loader=yaml.SafeLoader)
    return rule_yaml

def collect_rules():
    """Takes a baseline yaml file and parses the rules, returns a list of containing rules
    """
    all_rules = []
    #expected keys and references
    keys = ['mobileconfig',
            'macOS',
            'severity',
            'title',
            'check',
            'fix',
            'tags',
            'id',
            'references',
            'result',
            'discussion']
    references = ['disa_stig',
                  'cci',
                  'cce',
                  '800-53r4',
                  'srg']


    for rule in glob.glob('../rules/*/*.yaml'):
        rule_yaml = get_rule_yaml(rule)

        for key in keys:
            try:
                rule_yaml[key]
            except:
                #print "{} key missing ..for {}".format(key, rule)
                rule_yaml.update({key: "missing"})
            if key == "references":
                for reference in references:
                    try:
                        rule_yaml[key][reference]
                    except:
                        #print "expected reference '{}' is missing in key '{}' for rule{}".format(reference, key, rule)
                        rule_yaml[key].update({reference: ["None"]})

        all_rules.append(MacSecurityRule(rule_yaml['title'].replace('|', '\|'),
                                    rule_yaml['id'].replace('|', '\|'),
                                    rule_yaml['severity'].replace('|', '\|'),
                                    rule_yaml['discussion'].replace('|', '\|'),
                                    rule_yaml['check'].replace('|', '\|'),
                                    rule_yaml['fix'].replace('|', '\|'),
                                    rule_yaml['references']['cci'],
                                    rule_yaml['references']['cce'],
                                    rule_yaml['references']['800-53r4'],
                                    rule_yaml['references']['disa_stig'],
                                    rule_yaml['references']['srg'],
                                    rule_yaml['tags'],
                                    rule_yaml['result'],
                                    rule_yaml['mobileconfig'],
                                    rule_yaml['mobileconfig_info']
                                    ))

    return all_rules

def create_args():
    """configure the arguments used in the script, returns the parsed arguements
    """
    parser = argparse.ArgumentParser(
        description='Given a keyword tag, generate a generic baseline.yaml file containing rules with the tag.')
    parser.add_argument("-k", "--keyword", default=None,
                        help="Keyword tag to collect rules containing the tag.", action="store")
    parser.add_argument("-t", "--tags", default=None,
                        help="List the available keyword tags to search for.", action="store_true")
    
    return parser.parse_args()

def available_tags(all_rules):
    all_tags = []
    for rule in all_rules:
        for tag in rule.rule_tags:
            all_tags.append(tag)

    available_tags = []
    for tag in all_tags:
        if tag not in available_tags:
            available_tags.append(tag)

    available_tags.sort()

    for tag in available_tags:
        print(tag)
    return

def main():

    args = create_args()
    try:
        # output_basename = os.path.basename(args.baseline.name)
        # output_filename = os.path.splitext(output_basename)[0]
        # baseline_name = os.path.splitext(output_basename)[0].capitalize()
        file_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(file_dir)

        # stash current working directory
        original_working_directory = os.getcwd()

        all_rules = collect_rules()
        # switch to the scripts directory
        os.chdir(file_dir)

        if args.tags:
            available_tags(all_rules)
            return

        build_path = os.path.join(parent_dir, 'build', f'{args.keyword}')
        # if not (os.path.isdir(build_path)):
        #     try:
        #         os.makedirs(build_path)
        #     except OSError:
        #         print(f"Creation of the directory {build_path} failed")

    except IOError as msg:
        parser.error(str(msg))
    
    found_rules = []
    for rule in all_rules:
        if args.keyword in rule.rule_tags:
            found_rules.append(rule.rule_id)
    
    if len(found_rules) == 0:
        print("No rules found for the keyword provided, please verify from the following list:")
        available_tags(all_rules)
    else:
        for rule in found_rules:
            print(rule)
    # finally revert back to the prior directory
    os.chdir(original_working_directory)

if __name__ == "__main__":
    main()
