import FWCore.ParameterSet.Config as cms

PatEventJetProducer = cms.EDProducer("PatEventJetProducer",
    selector = cms.PSet(
        parameters = cms.PSet(),
        settings = cms.PSet(),
    ),

    Candidates = cms.InputTag("packedPFCandidates"),

    zSrc = cms.InputTag("ZMuMu", "Z"),
    zDaughterSrc = cms.InputTag("ZMuMu", "daughters"),

    verbose = cms.int32(0),
)

GenEventJetProducer = cms.EDProducer("GenEventJetProducer",
    selector = cms.PSet(
        parameters = cms.PSet(),
        settings = cms.PSet(),
    ),

    Candidates = cms.InputTag("packedGenParticles"),

    zSrc = cms.InputTag("ZMuMu", "Z"),
    zDaughterSrc = cms.InputTag("ZMuMu", "daughters"),

    verbose = cms.int32(0),
)
