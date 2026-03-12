import FWCore.ParameterSet.Config as cms

PatEventJetProducer = cms.EDProducer("PatEventJetProducer",
    selector = cms.PSet(
        parameters = cms.PSet(),
        settings = cms.PSet(),
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
        parameters = cms.PSet(),
        settings = cms.PSet(),
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
