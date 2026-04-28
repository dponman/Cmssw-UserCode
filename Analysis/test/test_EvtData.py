from SRothman.Analysis.common_cmsRun import *

from SRothman.Analysis.config.config import load_config
cfg = load_config('config_evt')

# Input source
if input_fname is None:
    input_fname = '/store/data/Run2018A/SingleMuon/MINIAOD/UL2018_MiniAODv2_GT36-v1/2820000/000EE25A-A8E8-1444-8A0B-0DBEBE5634FB.root'

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(input_fname),
    secondaryFileNames = cms.untracked.vstring(),
)

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '106X_dataRun2_v37', '')

# Shrink NANOAOD
from SRothman.Analysis.shrinkNano_cff import shrink_nanoAOD_data
process = shrink_nanoAOD_data(process)

# Path and EndPath definitions
process.nanoAOD_step = cms.Path(process.nanoSequence)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.NANOAODSIMoutput_step = cms.EndPath(process.NANOAODSIMoutput)

from SRothman.Analysis.setupEventSelections_cff import setupEventSelections
process = setupEventSelections(process, "linkedObjects:muons", config=cfg['EventSelection'], isMC=False)
# Schedule definition
process.schedule = cms.Schedule(process.selections_path,
                                process.nanoAOD_step,
                                process.endjob_step,
                                process.NANOAODSIMoutput_step)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

# customisation of the process.

# Automatic addition of the customisation function from PhysicsTools.NanoAOD.nano_cff
from PhysicsTools.NanoAOD.nano_cff import nanoAOD_customizeData

#call to customisation function nanoAOD_customizeData imported from PhysicsTools.NanoAOD.nano_cff
process = nanoAOD_customizeData(process)

from SRothman.Analysis.addParticlesTable_cff import addParticlesTable, addCollectionIndices
process = addParticlesTable(process,
    "ZMuMu:daughters",
    "ZMuMuMuons",
    singleton=False)
process = addCollectionIndices(process,
    "ZMuMu:daughters",
    "ZMuMuMuons",
    "linkedObjects:muons"
)
process = addParticlesTable(process,
    "ZMuMu:Z",
    "ZMuMuZ",
    singleton=True)

from SRothman.Analysis.setupAK8Jets_cff import setupAK8Jets
process = setupAK8Jets(process,
   isMC = False,
   skipJTB = False,
   genOnly = False,
   config=cfg)

from SRothman.CustomJets.setupEventJets import setupEventJets
process = setupEventJets(process,
    jets = 'selectedUpdatedJetsAK8',
    genjets = '',
    CHSjets = 'finalJets',
    name = 'ChargedEventJets',
    config = cfg,
    syst = 'NOM',
    isMC = False,
    genOnly = False
)

from SRothman.EECs.setupEEC import setupEEC_data
process = setupEEC_data(process,
    name = 'ChargedEECs',
    recojets = 'ChargedEventJets',
    whichEEC='proj',
    config = cfg['EECproj'],
    verbose = 0,
)

# End of customisation functions
