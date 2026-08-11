#!/usr/bin/env python3


import os
import sys
import copy
import yaml
from argparse import ArgumentParser
from http.client import HTTPException
from multiprocessing import Process

from CRABClient.UserUtilities import config, getUsername
from CRABAPI.RawCommand import crabCommand
from CRABClient.ClientExceptions import ClientException

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from production_tag import production_tag

requestname_base = getUsername()

output_site = "T3_CH_CERNBOX"
output_lfn_base = "/store/user/{username}/crab/{production_tag}".format(
    username=requestname_base,
    production_tag=production_tag,
)


def submit(cfg):
    print("DEBUG : In submit()")
    try:
        crabCommand('submit', config=cfg)
    except HTTPException as hte:
        print("Failed submitting task: %s" % (hte.headers,))
        print(hte)
    except ClientException as cle:
        print("Failed submitting task: %s" % (cle,))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-y', '--yaml', required=True, help='File with dataset descriptions')
    args = parser.parse_args()

    with open(args.yaml) as f:
        doc = yaml.safe_load(f)
        defaults = doc.get('defaults', {})

        for sample in sorted(doc["samples"].keys()):
            info = copy.deepcopy(defaults)
            info.update(doc["samples"][sample])
            print("\n\n*** Sample {} ***".format(sample))

            for dataset_shortname, dataset in info['datasets'].items():
                print("\n*** Submitting {}: {}".format(dataset_shortname, dataset))

                isMC = info.get("isMC", None)
                if isMC is None:
                    raise ValueError("Please specify parameter isMC")

                pset = info.get("pset", None)
                if pset is None:
                    raise ValueError("Please specify parameter pset")

                this_config = config()

                this_config.section_('General')
                this_config.General.transferOutputs = True
                this_config.General.transferLogs = True
                this_config.General.workArea = "crab/{}_{}/".format(requestname_base, production_tag)
                this_config.General.requestName = "{}_{}_{}_{}".format(
                    requestname_base, production_tag, info["year"], dataset_shortname
                )

                this_config.section_('JobType')
                this_config.JobType.pluginName = 'Analysis'
                this_config.JobType.psetName = os.path.expandvars(pset)
                this_config.JobType.allowUndistributedCMSSW = True
                this_config.JobType.numCores = 4
                this_config.JobType.maxMemoryMB = 8000
                this_config.JobType.sendExternalFolder = True
                globaltag = info.get("globaltag", None)
                this_config.JobType.pyCfgParams = [
                    'isMC={}'.format(isMC),
                    'reportEvery=1000',
                    'tag={}'.format(production_tag),
                    'globalTag={}'.format(globaltag),
                ]

                this_config.section_('User')
                this_config.section_('Site')
                this_config.Site.storageSite = output_site

                this_config.section_('Data')
                this_config.Data.publication = False
                this_config.Data.outLFNDirBase = "{}/{}/{}".format(output_lfn_base, info["year"], sample)
                this_config.Data.outputDatasetTag = dataset_shortname
                this_config.Data.inputDBS = 'global'
                this_config.Data.inputDataset = dataset

                splitting_mode = info.get("splitting", "Automatic")
                if splitting_mode not in ["Automatic", "FileBased", "LumiBased", "EventBased", "EventAwareLumiBased"]:
                    raise ValueError("Unrecognized splitting mode: {}".format(splitting_mode))
                this_config.Data.splitting = splitting_mode

                lumimask = info.get('lumimask', None)
                if lumimask:
                    this_config.Data.lumiMask = lumimask

                unitsPerJob = info.get("unitsPerJob", None)
                if unitsPerJob is not None:
                    this_config.Data.unitsPerJob = unitsPerJob

                totalUnits = info.get("totalUnits", None)
                if totalUnits is not None:
                    this_config.Data.totalUnits = totalUnits

                allowInvalid = info.get("allowInvalid", False)
                if allowInvalid:
                    this_config.Data.allowNonValidInputDataset = True

                print(this_config)
                p = Process(target=submit, args=(this_config,))
                p.start()
                p.join()
            print("*** Done with Sample {} ***\n\n".format(sample))
