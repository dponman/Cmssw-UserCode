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
#include "DataFormats/Math/interface/deltaR.h"
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

    edm::InputTag jetSrc_;
    edm::EDGetTokenT<edm::View<T>> jetSrcToken_;

    edm::InputTag pfCand_;
    edm::EDGetTokenT<edm::View<pat::PackedCandidate>> pfCandToken_;

    edm::InputTag CHSsrc_;
    edm::EDGetTokenT<edm::View<T>> CHSsrcToken_;
    bool addCHSindex_;
    double CHSmatchDR_;

    edm::InputTag zSrc_;
    edm::EDGetTokenT<edm::View<reco::CompositeCandidate>> zSrcToken_;

    edm::InputTag zDaughterSrc_;
    edm::EDGetTokenT<edm::View<reco::LeafCandidate>> zDaughterSrcToken_;

    int verbose_;
};

template <typename T>
EventJetProducerT<T>::EventJetProducerT(const edm::ParameterSet& conf) :
          selector_(conf.getParameter<edm::ParameterSet>("selector")),
          jetSrc_(conf.getParameter<edm::InputTag>("jetSrc")),
          jetSrcToken_(consumes<edm::View<T>>(jetSrc_)),
	  pfCand_(conf.getParameter<edm::InputTag>("pfCandidates")),
          pfCandToken_(consumes<edm::View<pat::PackedCandidate>>(pfCand_)),
          CHSsrc_(conf.getParameter<edm::InputTag>("CHSsrc")),
          CHSsrcToken_(consumes<edm::View<T>>(CHSsrc_)),
          addCHSindex_(conf.getParameter<bool>("addCHSindex")),
          CHSmatchDR_(conf.getParameter<double>("CHSmatchDR")),
          zSrc_(conf.getParameter<edm::InputTag>("zSrc")),
          zSrcToken_(consumes<edm::View<reco::CompositeCandidate>>(zSrc_)),
          zDaughterSrc_(conf.getParameter<edm::InputTag>("zDaughterSrc")),
          zDaughterSrcToken_(consumes<edm::View<reco::LeafCandidate>>(zDaughterSrc_)),
          verbose_(conf.getParameter<int>("verbose")){
    produces<std::vector<simon::jet>>();
}

template <typename T>
void EventJetProducerT<T>::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;

  edm::ParameterSetDescription selectorDesc;
  simon::particleSelector::fillPSetDescription(selectorDesc);
  desc.add<edm::ParameterSetDescription>("selector", selectorDesc);

  desc.add<edm::InputTag>("jetSrc");
  desc.add<edm::InputTag>("CHSsrc");
  desc.add<edm::InputTag>("pfCandidates");
  desc.add<bool>("addCHSindex");
  desc.add<double>("CHSmatchDR");
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
    edm::Handle<edm::View<T>> jets;
    evt.getByToken(jetSrcToken_, jets);

    edm::Handle<edm::View<pat::PackedCandidate>> candidates;
    evt.getByToken(pfCandToken_, candidates);

    edm::Handle<edm::View<T>> CHSjets;
    if(addCHSindex_){
        evt.getByToken(CHSsrcToken_, CHSjets);
    }

    std::cout << "EventJetProducer::produce called" << std::endl;
    auto result = std::make_unique<std::vector<simon::jet>>();
    simon::jet evt_jet;

    edm::Handle<edm::View<reco::CompositeCandidate>> zCands;
    evt.getByToken(zSrcToken_, zCands);

    edm::Handle<edm::View<reco::LeafCandidate>> zDaughters;
    evt.getByToken(zDaughterSrcToken_, zDaughters);

    float zpt = 1;
    if (zCands->empty()) {
        std::cout << "No Z candidate in event, setting jet pt to one." << std::endl;
    } else {
        zpt = zCands->at(0).pt();
        std::cout << "----------The zpt for this event (PRE BUILDING) is " << zpt << "-------------" << std::endl;
    }

    evt_jet.eta = 0;
    evt_jet.phi = 0;
    evt_jet.mass = 1;
    evt_jet.iJet = 0;

    std::vector<edm::Ptr<pat::PackedCandidate>> chargedPtrs;
    chargedPtrs.reserve(candidates->size());
    for (size_t i = 0; i < candidates->size(); ++i) {
        const auto& cand = candidates->at(i);
        if (cand.charge() == 0) continue;
        if (cand.pt() < 2) continue;
        bool isMuon = false;
        for (size_t j = 0; j < zDaughters->size(); ++j) {
            if (reco::deltaR(cand, zDaughters->at(j)) < 0.01) { isMuon = true; break; }
        }
        if (isMuon) continue;
        chargedPtrs.emplace_back(candidates->ptrAt(i));
    }

    selector_.buildJet(chargedPtrs, evt_jet);
    evt_jet.pt = zpt;
    std::cout << "+++++++++++The zpt for this event (POST BUILDING) is " << evt_jet.pt << "+++++++++" << std::endl;
    printf("###################################\n");
    printf("evt_jet is built\n");
    printf("###################################\n");
    result->clear();
    if (evt_jet.pt >= 40) {
        result->push_back(std::move(evt_jet));
    } else {
        printf("Skipping evt_jet with zpt = %.2f (< 40)\n", evt_jet.pt);
    }
    printf("result has %zu entries\n", result->size());
    evt.put(std::move(result));
    if(verbose_){
        printf("put into event\n");
    }
}  // end produce()

typedef EventJetProducerT<pat::Jet> PatEventJetProducer;
typedef EventJetProducerT<reco::GenJet> GenEventJetProducer;

DEFINE_FWK_MODULE(PatEventJetProducer);
DEFINE_FWK_MODULE(GenEventJetProducer);
