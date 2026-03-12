import FWCore.ParameterSet.Config as cms

from SRothman.CustomJets.systematics import *

_maxNumPart = 4096

from SRothman.Analysis.config.config import config

PatEventJetProducer = cms.EDProducer("PatEventJetProducer",
    selector = cms.PSet(
        parameters = systematics_parameters,
        settings = NOM,
    ),

    jetSrc = cms.InputTag("selectedPatJets"),
    pfCandidates = cms.InputTag("packedPFCandidates"),
    CHSsrc = cms.InputTag(""),
    addCHSindex = cms.bool(False),
    CHSmatchDR = cms.double(0.4),

    zSrc = cms.InputTag("ZMuMu", "Z"),
    zDaughterSrc = cms.InputTag("ZMuMu", "daughters"),

    verbose = cms.int32(1),
)

GenEventJetProducer = cms.EDProducer("GenEventJetProducer",
    selector = cms.PSet(
        parameters = systematics_parameters,
        settings = NOM,
    ),

    jetSrc = cms.InputTag("ak4GenJetsNoNu"),
    pfCandidates = cms.InputTag("packedPFCandidates"),

    CHSsrc = cms.InputTag(""),
    addCHSindex = cms.bool(False),
    CHSmatchDR = cms.double(0.4),

    zSrc = cms.InputTag("GenZDecay", "Z"),
    zDaughterSrc = cms.InputTag("GenZDecay", "daughters"),

    verbose = cms.int32(1),
)
