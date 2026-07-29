import FWCore.ParameterSet.Config as cms

from SRothman.CustomJets.EventJetProducer_cfi import GenEventJetProducer, PatEventJetProducer
from SRothman.CustomJets.EventJetTableProducer_cfi import EventJetTableProducer
from SRothman.Analysis.util import pyval_to_cmsval

def syst_params_from_config(config):
    result = cms.PSet()
    for key, value in config['parameters'].items():
        result.__setattr__(key, pyval_to_cmsval(value))
    return result

def syst_settings_from_config(config, syst):
    result = cms.PSet()
    for key, value in config['nominal'].items():
        result.__setattr__(key, pyval_to_cmsval(value))

    # Apply systematic variations
    if syst in config['variations']:
        for key, value in config['variations'][syst].items():
            result.__setattr__(key, pyval_to_cmsval(value))
    
        print("Settings for systematic variation %s:" % syst)
        for key in result.parameterNames_():
            print("  %s: %s" % (key, getattr(result, key)))

    elif syst != 'NOM':
        raise ValueError("Systematic variation %s not found in config." % syst)
    
    return result

def selector_from_config(config, syst):
    parameters = syst_params_from_config(config)
    settings = syst_settings_from_config(config, syst)
    return cms.PSet(
        parameters = parameters,
        settings = settings,
    )

def setupGenEventJets(process,
                      name,
                      config):

    setattr(process, 'Gen'+name, GenEventJetProducer.clone(
        verbose = False,
        selector = selector_from_config(config['Systematics'], 'NOM')
    ))

    setattr(process, 'Gen'+name+'Table', EventJetTableProducer.clone(
        src = 'Gen'+name,
        name = 'Gen'+name,
        verbose=False,
    ))

    setattr(process, name+"MCTask", cms.Task(
        getattr(process, 'Gen'+name),
        getattr(process, 'Gen'+name+'Table')
    ))
    process.schedule.associate(getattr(process, name+'MCTask'))

    return process

def setupRecoEventJets(process,
                       name,
                       config,
                       syst):

    setattr(process, name, PatEventJetProducer.clone(
        verbose = False,
        selector = selector_from_config(config['Systematics'], syst)
    ))

    setattr(process, name+"Preselection", cms.EDProducer("JetSelectionFlagTranslator",
        target = cms.InputTag(name),
        verbose = cms.int32(0)
    ))

    setattr(process, name+"OverlapVeto", cms.EDProducer("JetSelectionFlagTranslator",
        target = cms.InputTag(name),
        verbose = cms.int32(0)
    ))

    setattr(process, name+'Table', EventJetTableProducer.clone(
        src = name,
        name = name,
        verbose=False,
    ))

    setattr(process, name+"CHSTable", cms.EDProducer("CHSSumTableProducer",
        src = cms.InputTag(name),
        name = cms.string(name+"BK"),
        verbose = cms.int32(0)
    ))

    setattr(process, name+'Task', cms.Task(
        getattr(process, name),
        getattr(process, name+'Preselection'),
        getattr(process, name+'OverlapVeto'),
        getattr(process, name+'Table'),
    ))
    process.schedule.associate(getattr(process, name+'Task'))

    return process

def setupEventJets(process, 
                   name,
                   config,
                   syst,
                   isMC,
                   genOnly):
    if isMC:
        process = setupGenEventJets(process,
                                    name,
                                    config)
    if not genOnly:
        process = setupRecoEventJets(process,
                                     name,
                                     config,
                                     syst)
    return process



