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

    int verbose_;
};

template <typename T>
EventJetProducerT<T>::EventJetProducerT(const edm::ParameterSet& conf) :
          selector_(conf.getParameter<edm::ParameterSet>("selector")),
	  Cand_(conf.getParameter<edm::InputTag>("Candidates")),
          CandToken_(consumes<edm::View<T>>(Cand_)),

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

    std::cout << "EventJetProducer::produce called" << std::endl;    
    auto result = std::make_unique<std::vector<simon::jet>>();
    simon::jet evt_jet;
        
    size_t mu1 = 999999;
    size_t mu2 = 999999;
    float pt1 = -1.0;
    float pt2 = -1.0;
    float zpt = 0.0;

    for (size_t i = 0; i < candidates->size(); ++i) {
       const auto& cand = candidates->at(i);
       if (std::abs(cand.pdgId()) != 13) continue;

       float pt = cand.pt();
       if (pt > pt1) {
           pt2 = pt1;
           mu2 = mu1;
           pt1 = pt;
           mu1 = i;
       } else if (pt > pt2) {
           pt2 = pt;
           mu2 = i;
       }
    }



    if (mu1 == 999999 || mu2 == 999999) {
    evt_jet.pt = 1;
    std::cout << "Fewer than two muons in event, setting jet pt to one." << std::endl;
    }
    else {
    const auto& cand1 = candidates->at(mu1);
    const auto& cand2 = candidates->at(mu2);
    evt_jet.pt = std::sqrt(std::pow((cand1.pt()*std::cos(cand1.phi())+cand2.pt()*std::cos(cand2.phi())), 2)+std::pow((cand1.pt()*std::sin(cand1.phi())+cand2.pt()*std::sin(cand2.phi())),2));
    std::cout << "----------The zpt for this event (PRE BUILDING) is " << evt_jet.pt << "-------------" << std::endl;
    }
//   cand1 = candidates->at(mu1);
//   cand2 = candidates->at(mu2);
//   evt_jet.pt = std::sqrt(std::pow((cand1.pt()*std::cos(cand1.phi())+cand2.pt()*std::cos(cand2.phi())), 2)+std::pow((cand1.pt()*std::sin(cand1.phi())+cand2.pt()*std::sin(cand2.phi())),2));
//   std::cout << "----------The zpt for this event (PRE BUILDING) is " << evt_jet.pt << "-------------" << std::endl;
//   if (mu1 == 999999 || mu2 == 999999) {
//   	evt_jet.pt = 0;
//       std::cout << "Fewer than two muons in event, setting jet pt to zero." << std::endl;
//   }
    evt_jet.eta = 0;
    evt_jet.phi = 0;
    evt_jet.mass = 1;
    evt_jet.iJet = 0;

    std::vector<edm::Ptr<pat::PackedCandidate>> chargedPtrs;
    chargedPtrs.reserve(candidates->size());
    for (size_t i = 0; i < candidates->size(); ++i) {
        const auto& cand = candidates->at(i);
        if (cand.charge() == 0) continue;
	if (i == mu1 || i == mu2) continue;
	if (cand.pt() < 2) continue;
        chargedPtrs.emplace_back(candidates->ptrAt(i));
    }

    selector_.buildJet(chargedPtrs, evt_jet, 0, 0, 0);
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

typedef EventJetProducerT<pat::PackedCandidate> PatEventJetProducer;
typedef EventJetProducerT<pat::PackedGenParticle> GenEventJetProducer;

DEFINE_FWK_MODULE(PatEventJetProducer);
DEFINE_FWK_MODULE(GenEventJetProducer);
