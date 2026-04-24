# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: NANO -s NANO --mc --conditions 106x_mc2017_realistic_v9-v2 --era Run2_2017,run2_nanoAOD_106Xv2 --eventcontent NANOAODSIM --datatier NANOAODSIM --customise_commands=process.add_(cms.Service('InitRootHandlers', EnableIMT = cms.untracked.bool(False)));process.MessageLogger.cerr.FwkReport.reportEvery=1000 -n -1 --no_exec
import FWCore.ParameterSet.Config as cms

from Configuration.Eras.Era_Run2_2018_cff import Run2_2018
from Configuration.Eras.Modifier_run2_nanoAOD_106Xv2_cff import run2_nanoAOD_106Xv2

RUNNING_CRAB = True
#configname = 'config_genonly'
configname = 'config'

if not RUNNING_CRAB:
    from FWCore.ParameterSet.VarParsing import VarParsing

    options = VarParsing ('analysis')
    options.register('index',
                  -1,
                  VarParsing.multiplicity.singleton,
                  VarParsing.varType.int,
                  "Input file index")
    options.register('filelist',
                     '',
                     VarParsing.multiplicity.singleton,
                     VarParsing.varType.string,
                     "Input file list")
    options.register('N',
                     20,
                     VarParsing.multiplicity.singleton,
                     VarParsing.varType.int,
                     'Number of events to process')
    options.register('Threads',
                     1,
                     VarParsing.multiplicity.singleton,
                     VarParsing.varType.int,
                     'Number of threads to use')
    options.parseArguments()
else:
    options = {
        'index': -1,
        'filelist': '',
        'N': -1,
        'Threads': 4
    }
    from argparse import Namespace
    options = Namespace(**options)

if options.index >= 0:
    selected_fname = 'NANO_selected_%d.root' % options.index
    dropped_fname = 'NANO_dropped_%d.root' % options.index

    if len(options.filelist) == 0:
        raise ValueError('filelist option is required when index is specified')

    with open(options.filelist, 'r') as f:
        fnames = f.readlines()
        if options.index >= len(fnames):
            raise ValueError('filelist does not have enough entries for index')
        input_fname = fnames[options.index].strip()
else:
    input_fname = None
    selected_fname = 'NANO_selected.root'
    dropped_fname = 'NANO_dropped.root'

process = cms.Process('NANO',Run2_2018,run2_nanoAOD_106Xv2)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('PhysicsTools.NanoAOD.nano_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(options.N)
)

process.options = cms.untracked.PSet(

)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('NANO nevts:-1'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition
process.NANOAODSIMoutput = cms.OutputModule("NanoAODOutputModule",
    compressionAlgorithm = cms.untracked.string('LZMA'),
    compressionLevel = cms.untracked.int32(9),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('NANOAODSIM'),
        filterName = cms.untracked.string('')
    ),
    SelectEvents = cms.untracked.PSet( 
        SelectEvents = cms.vstring('selections_path')
    ),
    fileName = cms.untracked.string(selected_fname),
    outputCommands = process.NANOAODSIMEventContent.outputCommands,
)

process.NANOAODoutput = cms.OutputModule("NanoAODOutputModule",
    compressionAlgorithm = cms.untracked.string('LZMA'),
    compressionLevel = cms.untracked.int32(9),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('NANOAOD'),
        filterName = cms.untracked.string('')
    ),
    SelectEvents = cms.untracked.PSet( 
        SelectEvents = cms.vstring('selections_path')
    ),
    fileName = cms.untracked.string(selected_fname),
    outputCommands = process.NANOAODEventContent.outputCommands,
)

process.DroppedEventsSimOutput = cms.OutputModule("NanoAODOutputModule",
    compressionAlgorithm = cms.untracked.string('LZMA'),
    compressionLevel = cms.untracked.int32(9),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('NANOAODSIM'),
        filterName = cms.untracked.string('')
    ),
    fileName = cms.untracked.string(dropped_fname),
    outputCommands = cms.untracked.vstring(
        'drop *',
        'keep nanoaodFlatTable_genTable_*_*',
        'keep nanoaodFlatTable_genWeightsTable_*_*',
        'keep nanoaodFlatTable_lheInfoTable_*_*'
    ),
    SelectEvents = cms.untracked.PSet(
        SelectEvents = cms.vstring('!selections_path')
    )
)

#Setup FWK for multithreaded
process.options.numberOfThreads=cms.untracked.uint32(options.Threads)
process.options.numberOfStreams=cms.untracked.uint32(options.Threads)
process.options.numberOfConcurrentLuminosityBlocks=cms.untracked.uint32(1)

process.MessageLogger.cerr.FwkReport.reportEvery=1

process.add_(cms.Service('InitRootHandlers', EnableIMT = cms.untracked.bool(False)));
# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion
