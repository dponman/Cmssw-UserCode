import FWCore.ParameterSet.Config as cms

EECProjVectorTableProducer = cms.EDProducer("EECProjVectorTableProducer",
    name = cms.string(""),
    maxOrder = cms.uint32(3),
    EECs = cms.InputTag("")
)

EECProjUnbinnedTableProducer = cms.EDProducer("EECProjUnbinnedTableProducer",
    name = cms.string(""),
    maxOrder = cms.uint32(3),
    EECs = cms.InputTag("")
)

EECProjArrayTableProducer = cms.EDProducer("EECProjArrayTableProducer",
    name = cms.string(""),
    maxOrder = cms.uint32(3),
    EECs = cms.InputTag("")
)

