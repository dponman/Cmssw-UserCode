import FWCore.ParameterSet.Config as cms

EECProjTransferVectorTableProducer = cms.EDProducer("EECProjTransferVectorTableProducer",
    name = cms.string(""),
    maxOrder = cms.uint32(6),
    EECTransfer = cms.InputTag("")
)

EECProjTransferUnbinnedTableProducer = cms.EDProducer("EECProjTransferUnbinnedTableProducer",
    name = cms.string(""),
    maxOrder = cms.uint32(6),
    EECTransfer = cms.InputTag("")
)

EECProjTransferArrayTableProducer = cms.EDProducer("EECProjTransferArrayTableProducer",
    name = cms.string(""),
    maxOrder = cms.uint32(6),
    EECTransfer = cms.InputTag("")
)

