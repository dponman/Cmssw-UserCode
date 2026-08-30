from SRothman.Analysis.common_cmsRun import *

from SRothman.Analysis.config.config import load_config
cfg = load_config('config_basic')

# Input source
if input_fname is None:
    input_fname = '/store/mc/RunIISummer20UL18MiniAODv2/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/120000/015753DA-CD2E-F546-9A7B-9DD451DEA159.root'

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(input_fname),
    secondaryFileNames = cms.untracked.vstring(),
    #eventsToProcess = cms.untracked.VEventRange(cms.EventRange(1, 2339661, 1, 2339661))
)

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '106X_upgrade2018_realistic_v16_L1v1', '')

# Shrink NANOAOD
from SRothman.Analysis.shrinkNano_cff import shrink_nanoAOD_MC
process = shrink_nanoAOD_MC(process)

# Path and EndPath definitions
process.nanoAOD_step = cms.Path(process.nanoSequenceMC)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.NANOAODSIMoutput_step = cms.EndPath(process.NANOAODSIMoutput)
process.DroppedEventsSimOutput_step = cms.EndPath(process.DroppedEventsSimOutput)

# ABOVE IS STANDARD NANO

# BELOW IS ME :)

from SRothman.Analysis.setupEventSelections_cff import setupRecoEventSelections, setupGenEventSelections
process, recoSelPath = setupRecoEventSelections(process, "linkedObjects:muons", isMC=True, config=cfg['EventSelection'])
process, genSelPath = setupGenEventSelections(process, "prunedGenParticles", config=cfg['EventSelection'])

process.NANOAODSIMoutput.SelectEvents.SelectEvents = cms.vstring(recoSelPath, genSelPath)

# Schedule definition
process.schedule = cms.Schedule(getattr(process, recoSelPath),
                                getattr(process, genSelPath),
                                process.nanoAOD_step,
                                process.endjob_step,
                                process.NANOAODSIMoutput_step)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

# customisation of the process.

# Automatic addition of the customisation function from PhysicsTools.NanoAOD.nano_cff
from PhysicsTools.NanoAOD.nano_cff import nanoAOD_customizeMC

#call to customisation function nanoAOD_customizeMC imported from PhysicsTools.NanoAOD.nano_cff
process = nanoAOD_customizeMC(process)

from SRothman.Analysis.addParticlesTable_cff import addParticlesTable
process = addParticlesTable(process,
    "ZMuMureco:daughters",
    "ZMuMuMuons",
    singleton=False,
    skipNonExistingSrc=True)
process = addParticlesTable(process,
    "ZMuMureco:Z",
    "ZMuMuZ",
    skipNonExistingSrc=True,
    singleton=False)

from SRothman.CustomJets.setupEventJets import setupEventJets
for syst in ['NOM', 'CH_UP', 'CH_DN', 'TRK_EFF']:
    suffix = syst.replace('_', ''); # remove underscores for the suffix
    process = setupEventJets(process,
        name = 'ChargedEventJets'+suffix,
        config = cfg,
        syst = syst,
        isMC = True,
        genOnly = False,
        recoZMuMuLabel = 'ZMuMureco',
        genZMuMuLabel = 'ZMuMugen',
    )

    from SRothman.Matching.setupMatching import setupMatching
    process = setupMatching(process,
        name = 'ChargedGenMatch'+suffix,
        reco = 'ChargedEventJets'+suffix,
        gen = 'GenChargedEventJets'+suffix,
        config = cfg['Matching']
    )

    from SRothman.EECs.setupEEC import setupEEC_MC
    # EventJets don't produce Preselection/OverlapVeto flag collections, unlike SimonJets
    evtjet_eecproj_cfg = dict(cfg['EECproj'], flags=[])
    process = setupEEC_MC(process,
        name = 'ChargedEECs'+suffix,
        genMatch = 'ChargedGenMatch'+suffix,
        genjets = 'GenChargedEventJets'+suffix,
        recojets = 'ChargedEventJets'+suffix,
        whichEEC='proj',
        config = evtjet_eecproj_cfg,
        verbose = 0,
    )
