import FWCore.ParameterSet.Config as cms

from SRothman.Analysis.CorrectedMuonProducer_cfi import CorrectedMuonProducer
from SRothman.Analysis.RoccoRValueMapProducer_cfi import RoccoRValueMapProducer
from SRothman.Analysis.ZMuMuEventSelectionFilter_cfi import getZMuMuFilter


def _build_selection_chain(process, muons, isMC, config, genmuons, label):
    suffix = label if label else ''

    if not genmuons:
        process.RoccoR = RoccoRValueMapProducer.clone(
            src = cms.InputTag(muons),
            isMC = isMC
        )

        process.muonTable.externalVariables.RoccoR = cms.PSet(
            compression = cms.string('none'),
            doc = cms.string("Rochester correction factor"),
            mcOnly = cms.bool(False),
            precision = cms.int32(-1),
            src = cms.InputTag("RoccoR"),
            type = cms.string('float')
        )

        selectorclass = "PATMuonSelector"
    else:
        selectorclass = "GenParticleSelector"

    muoncut = ''
    if config['maxMuEta'] > 0:
        muoncut += "abs(eta) < %0.2f && "%config['maxMuEta']
    if config['subMuPt'] > 0:
        muoncut += " pt > %0.2f && "%config['subMuPt']
    if not genmuons:
        if config['muID'] not in ['', 'none']:
            muoncut += " passed('%s') && "%config['muID']
        if config['muISO'] not in ['', 'none']:
            muoncut += " passed('%s') && "%config['muISO']
        if config['muDZ'] > 0:
            muoncut += " abs(dB('PVDZ')) < %0.2f && "%config['muDZ']
        if config['muDXY'] > 0:
            muoncut += " abs(dB('PV2D')) < %0.2f && "%config['muDXY']

    if muoncut.endswith(' && '):
        muoncut = muoncut[:-4]  # remove trailing ' && '

    selectedMuonsName = 'SelectedMuons' + suffix
    setattr(process, selectedMuonsName, cms.EDFilter(
        selectorclass,
        src = cms.InputTag(muons),
        cut = cms.string(muoncut)
    ))

    diMuonFilterName = 'DiMuonFilter' + suffix
    setattr(process, diMuonFilterName, cms.EDFilter(
        "CandViewCountFilter",
        src = cms.InputTag(selectedMuonsName),
        minNumber = cms.uint32(2)
    ))

    zMuMuName = 'ZMuMu' + suffix
    setattr(process, zMuMuName, getZMuMuFilter(config, cms.InputTag(selectedMuonsName)))

    path = []
    if not genmuons:
        path.append(process.RoccoR)
    path.append(getattr(process, selectedMuonsName))
    path.append(getattr(process, diMuonFilterName))
    path.append(getattr(process, zMuMuName))

    if config['maxMET'] > 0:
        metSelectorName = 'METselector' + suffix
        setattr(process, metSelectorName, cms.EDFilter(
            'CandViewSelector',
            src = cms.InputTag('slimmedMETsPuppi'),
            cut = cms.string('pt < %f' % config['maxMET'])
        ))
        metFilterName = 'METfilter' + suffix
        setattr(process, metFilterName, cms.EDFilter(
            'CandViewCountFilter',
            src = cms.InputTag(metSelectorName),
            minNumber = cms.uint32(1)
        ))
        path.append(getattr(process, metSelectorName))
        path.append(getattr(process, metFilterName))

    return path


def _attach_path(process, path, label):
    suffix = ('_' + label) if label else ''
    pathName = 'selections_path' + suffix
    thePath = cms.Path()
    for module in path:
        thePath += module
    setattr(process, pathName, thePath)
    return pathName


def setupRecoEventSelections(process, muons, isMC, config, label='reco'):
    path = _build_selection_chain(process, muons, isMC, config, genmuons=False, label=label)
    pathName = _attach_path(process, path, label)
    return process, pathName


def setupGenEventSelections(process, genparticles, config, label='gen'):
    path = _build_selection_chain(process, genparticles, isMC=True, config=config, genmuons=True, label=label)
    pathName = _attach_path(process, path, label)
    return process, pathName


def setupEventSelections(process,
                         muons,
                         isMC,
                         config,
                         genmuons=False):
    path = _build_selection_chain(process, muons, isMC, config, genmuons=genmuons, label='')
    _attach_path(process, path, label='')
    return process
