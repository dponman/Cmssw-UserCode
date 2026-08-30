from bz2 import compress
import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.common_cff import *

def addParticlesTable(process,
                      src,
                      name,
                      singleton=False,
                      skipNonExistingSrc=False):

    setattr(process, name+"particlesTable", cms.EDProducer("SimpleCandidateFlatTableProducer",
        src = cms.InputTag(src),
        cut = cms.string(""),
        name = cms.string(name),
        doc = cms.string("Basic candidate table"),
        singleton=cms.bool(singleton),
        extension=cms.bool(False),
        skipNonExistingSrc=cms.bool(skipNonExistingSrc),
        externalVariables = cms.PSet(),
        variables=cms.PSet(
            pt = Var("pt", float, doc="pt", precision=-1),
            eta = Var("eta", float, doc="eta", precision=-1),
            phi = Var("phi", float, doc="phi", precision=-1),
            mass = Var("mass", float, doc="mass", precision=-1),
            pdgId = Var("pdgId", int, doc="pdgId", precision=-1),
            charge = Var("charge", int, doc="charge", precision=-1),
        )))

    setattr(process, name+'particlesTableTask', cms.Task(getattr(process, name+'particlesTable')))
    process.schedule.associate(getattr(process, name+'particlesTableTask'))

    return process

def addCollectionIndices(process, 
                         src, 
                         name,
                         collection):
    setattr(process, name+"collectionIndexProducer", 
            cms.EDProducer("LeafCandidateCollectionIndexProducer",
                src = cms.InputTag(src),
                searchCollection = cms.InputTag(collection),
            )
    )
    setattr(process, name+'collectionIndexTask', cms.Task(getattr(process, name+"collectionIndexProducer")))
    process.schedule.associate(getattr(process, name+'collectionIndexTask'))

    getattr(process, name+"particlesTable").externalVariables.collectionIndex = cms.PSet(
        compression = cms.string('none'),
        doc = cms.string("Index of the particle in the original collection"),
        mcOnly = cms.bool(False),
        precision = cms.int32(-1),
        src = cms.InputTag(name+"collectionIndexProducer"),
        type = cms.string('int')
    )

    return process