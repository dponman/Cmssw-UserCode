import FWCore.ParameterSet.Config as cms

from SRothman.CustomJets.systematics import *

_maxNumPart = 4096

from SRothman.Analysis.config.config import config

PatEventJetProducer = cms.EDProducer("PatEventJetProducer",
    selector = cms.PSet(
        parameters = systematics_parameters,
        settings = NOM,
    ),

    Candidates = cms.InputTag("packedPFCandidates"),

    verbose = cms.int32(1),
)

GenEventJetProducer = cms.EDProducer("GenEventJetProducer",
    selector = cms.PSet(
        parameters = systematics_parameters,
        settings = NOM,
    ),

    Candidates = cms.InputTag("packedGenParticles"),

    verbose = cms.int32(1),
)
