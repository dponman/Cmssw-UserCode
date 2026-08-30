#include "DataFormats/Common/interface/Handle.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/Utilities/interface/EDGetToken.h"
#include "FWCore/Framework/interface/ConsumesCollector.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "DataFormats/EgammaCandidates/interface/GsfElectron.h"
#include "DataFormats/EgammaCandidates/interface/GsfElectronFwd.h"
#include "DataFormats/PatCandidates/interface/Electron.h"
#include "DataFormats/Common/interface/ValueMap.h"
#include "DataFormats/JetReco/interface/PFJet.h"
#include "DataFormats/PatCandidates/interface/Jet.h"
#include "DataFormats/PatCandidates/interface/Muon.h"
#include "DataFormats/NanoAOD/interface/FlatTable.h"
#include "DataFormats/Math/interface/deltaR.h"
#include "DataFormats/PatCandidates/interface/PackedCandidate.h"
#include "DataFormats/PatCandidates/interface/PackedGenParticle.h"
#include "DataFormats/Candidate/interface/CompositeCandidate.h"
#include "DataFormats/Candidate/interface/LeafCandidate.h"

#include "SRothman/SimonTools/src/jet.h"
#include "SRothman/SimonTools/src/util.h"

#include "SRothman/SimonTools/src/isID.h"
#include "SRothman/SimonTools/src/particleSelector.h"

#include <iostream>
#include <memory>
#include <vector>
#include <cmath>

template <typename T>
class EventJetProducerT : public edm::stream::EDProducer<> {
public:
    explicit EventJetProducerT(const edm::ParameterSet&);
    ~EventJetProducerT() override {}
    static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);
    void produce(edm::Event&, const edm::EventSetup&) override;
private:
    simon::particleSelector selector_;

    edm::InputTag Cand_;
    edm::EDGetTokenT<edm::View<T>> CandToken_;

    edm::InputTag zSrc_;
    edm::EDGetTokenT<edm::View<reco::CompositeCandidate>> zSrcToken_;

    edm::InputTag zDaughterSrc_;
    edm::EDGetTokenT<edm::View<reco::LeafCandidate>> zDaughterSrcToken_;

    int verbose_;
};

template <typename T>
EventJetProducerT<T>::EventJetProducerT(const edm::ParameterSet& conf) :
          selector_(conf.getParameter<edm::ParameterSet>("selector")),
          Cand_(conf.getParameter<edm::InputTag>("Candidates")),
          CandToken_(consumes<edm::View<T>>(Cand_)),
          zSrc_(conf.getParameter<edm::InputTag>("zSrc")),
          zSrcToken_(mayConsume<edm::View<reco::CompositeCandidate>>(zSrc_)),
          zDaughterSrc_(conf.getParameter<edm::InputTag>("zDaughterSrc")),
          zDaughterSrcToken_(mayConsume<edm::View<reco::LeafCandidate>>(zDaughterSrc_)),
          verbose_(conf.getParameter<int>("verbose")){
    produces<std::vector<simon::jet>>();
}

template <typename T>
void EventJetProducerT<T>::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;

  edm::ParameterSetDescription selectorDesc;
  simon::particleSelector::fillPSetDescription(selectorDesc);
  desc.add<edm::ParameterSetDescription>("selector", selectorDesc);

  desc.add<edm::InputTag>("Candidates");
  desc.add<edm::InputTag>("zSrc");
  desc.add<edm::InputTag>("zDaughterSrc");

  desc.add<int>("verbose");

  descriptions.addWithDefaultLabel(desc);
}

template <typename T>
void EventJetProducerT<T>::produce(edm::Event& evt,
                                   const edm::EventSetup& setup) {
    if(verbose_){
        printf("top of EventJetProducerT<T>::produce()\n");
    }
    edm::Handle<edm::View<T>> candidates;
    evt.getByToken(CandToken_, candidates);

    edm::Handle<edm::View<reco::CompositeCandidate>> zCands;
    evt.getByToken(zSrcToken_, zCands);

    edm::Handle<edm::View<reco::LeafCandidate>> zDaughters;
    evt.getByToken(zDaughterSrcToken_, zDaughters);

    auto result = std::make_unique<std::vector<simon::jet>>();
    simon::jet evt_jet;

    float zpt = 1;
    if (!zCands.isValid() || zCands->empty()) {
        if(verbose_){
            printf("No Z candidate in event, setting jet pt to one.\n");
        }
    } else {
        zpt = zCands->at(0).pt();
    }

    evt_jet.pt = zpt;
    evt_jet.eta = 0;
    evt_jet.phi = 0;
    evt_jet.mass = 1;
    evt_jet.iJet = 0;

    std::vector<edm::Ptr<T>> chargedPtrs;
    chargedPtrs.reserve(candidates->size());
    for (size_t i = 0; i < candidates->size(); ++i) {
        const auto& cand = candidates->at(i);
        if (cand.charge() == 0) continue;
        if (cand.pt() < 2) continue;
        bool isMuon = false;
        if (zDaughters.isValid()) {
            for (size_t j = 0; j < zDaughters->size(); ++j) {
                if (reco::deltaR(cand, zDaughters->at(j)) < 0.01) { isMuon = true; break; }
            }
        }
        if (isMuon) continue;
        chargedPtrs.emplace_back(candidates->ptrAt(i));
    }

    selector_.buildJet(chargedPtrs, evt_jet, evt_jet.pt, evt_jet.eta, evt_jet.phi);

    if(verbose_){
        printf("evt_jet is built, pt = %f\n", evt_jet.pt);
    }

    if (evt_jet.pt >= 40) {
        result->push_back(std::move(evt_jet));
    } else if(verbose_){
        printf("Skipping evt_jet with pt = %.2f (< 40)\n", evt_jet.pt);
    }

    evt.put(std::move(result));
    if(verbose_){
        printf("put into event\n");
    }
}  // end produce()

typedef EventJetProducerT<pat::PackedCandidate> PatEventJetProducer;
typedef EventJetProducerT<pat::PackedGenParticle> GenEventJetProducer;

DEFINE_FWK_MODULE(PatEventJetProducer);
DEFINE_FWK_MODULE(GenEventJetProducer);
