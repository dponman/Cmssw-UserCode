#include "DataFormats/Common/interface/Handle.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/Utilities/interface/EDGetToken.h"
#include "FWCore/Utilities/interface/Exception.h"
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

#include "SRothman/DataFormats/interface/EEC.h"

#include "SRothman/EECs/src/ProjResult.h"

template <class ResultType>
class EECProjTableProducer : public edm::stream::EDProducer<> {
public:
    explicit EECProjTableProducer(const edm::ParameterSet&);
    ~EECProjTableProducer() override = default;
    static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);
    void produce(edm::Event&, const edm::EventSetup&) override;
private:
    std::string name_;
    unsigned maxOrder_;

    edm::EDGetTokenT<std::vector<ResultType>> EECToken_;
};

template <class ResultType>
EECProjTableProducer<ResultType>::EECProjTableProducer(const edm::ParameterSet& conf) :
        name_(conf.getParameter<std::string>("name")),
        maxOrder_(conf.getParameter<unsigned>("maxOrder")),
        EECToken_(consumes<std::vector<ResultType>>(conf.getParameter<edm::InputTag>("EECs"))) {

    if (maxOrder_ < 2) {
        throw cms::Exception("Configuration")
            << "Parameter 'maxOrder' must be >= 2, got " << maxOrder_;
    }

    for (unsigned order = 2; order <= maxOrder_; ++order) {
        produces<nanoaod::FlatTable>(name_ + "Order" + std::to_string(order));
    }
    produces<nanoaod::FlatTable>(name_+"BK");
}

template <class ResultType>
void EECProjTableProducer<ResultType>::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    edm::ParameterSetDescription desc;

    desc.add<std::string>("name");
    desc.add<unsigned>("maxOrder");
    desc.add<edm::InputTag>("EECs");
    descriptions.addWithDefaultLabel(desc);
}

template <class ResultType>
void EECProjTableProducer<ResultType>::produce(edm::Event& event, const edm::EventSetup& setup){
    edm::Handle<std::vector<ResultType>> EECs;
    event.getByToken(EECToken_, EECs);

    if (!EECs->empty()) {
        const auto availableMaxOrder = EECs->front().result.get_data().size() + 1;
        if (maxOrder_ > availableMaxOrder) {
            throw cms::Exception("Configuration")
                << "Configured maxOrder=" << maxOrder_
                << " exceeds available result order " << availableMaxOrder;
        }
    }

    const unsigned nOrders = maxOrder_ - 1;

    std::vector<int> nR;
    std::vector<std::vector<int>> nEntry(nOrders);

    std::vector<int> iJet, iReco;
    std::vector<float> pt_denom;

    for (unsigned order = 2; order <= maxOrder_; ++order){
        const unsigned orderIndex = order - 2;
        const std::string orderName = "Order" + std::to_string(order);
        std::vector<typename ResultType::T> R;
        std::vector<float> wt;

        for (const auto& EEC : *EECs){
            const auto& data = EEC.result.get_data()[orderIndex];

            if (order==2){
                nR.push_back(data.nR);

                iJet.push_back(EEC.iJet);
                iReco.push_back(EEC.iReco);
                pt_denom.push_back(EEC.result.get_pt_denom());
            }

            if constexpr (ResultType::IS_ARRAY){
                int entries = 0;
                for (unsigned iR = 0; iR < data.get_data().size(); ++iR){
                    if (data.get_data()[iR] > 0){
                        entries++;
                        R.push_back(iR);
                        wt.push_back(data.get_data()[iR]);
                    }
                }
                if (entries == 0){
                    nEntry[orderIndex].push_back(1);
                    R.push_back(-1);
                    wt.push_back(-1);
                } else {
                    nEntry[orderIndex].push_back(entries);
                }
            } else {
                if (data.get_data().empty()){
                    nEntry[orderIndex].push_back(1);
                    R.push_back(-1);  
                    wt.push_back(-1);
                } else {
                    nEntry[orderIndex].push_back(data.get_data().size());
                    for (const auto& [iR, iwt] : data.get_data()){
                        R.push_back(iR);
                        wt.push_back(iwt);
                    }
                }
            }
        }

        auto dataTable = std::make_unique<nanoaod::FlatTable>(R.size(), name_ + orderName, false);
        dataTable->template addColumn<typename ResultType::T>("R", R, "R values", ResultType::COLUMN_TYPE);
        dataTable->template addColumn<float>("wt", wt, "wt values", nanoaod::FlatTable::FloatColumn);
        event.put(std::move(dataTable), name_ + orderName);
    }

    auto BKTable = std::make_unique<nanoaod::FlatTable>(nR.size(), name_ + "BK", false);    
    BKTable->addColumn<int>("nR", nR, "nR", nanoaod::FlatTable::IntColumn);
    BKTable->addColumn<int>("iJet", iJet, "iJet", nanoaod::FlatTable::IntColumn);
    BKTable->addColumn<int>("iReco", iReco, "iReco", nanoaod::FlatTable::IntColumn);
    BKTable->addColumn<float>("pt_denom", pt_denom, "pt_denom", nanoaod::FlatTable::FloatColumn);
    for (unsigned order = 2; order <= maxOrder_; ++order){
        const unsigned orderIndex = order - 2;
        const std::string orderName = "Order" + std::to_string(order);
        BKTable->addColumn<int>("nEntry" + orderName, nEntry[orderIndex], "nEntry", nanoaod::FlatTable::IntColumn);
    }
    event.put(std::move(BKTable), name_ + "BK");
}

typedef EECProjTableProducer<EEC::CMSSWResult<EEC::ProjResult<EEC::ProjVectorContainer<double>>>> EECProjUnbinnedTableProducer;
typedef EECProjTableProducer<EEC::CMSSWResult<EEC::ProjResult<EEC::ProjVectorContainer<unsigned>>>> EECProjVectorTableProducer;
typedef EECProjTableProducer<EEC::CMSSWResult<EEC::ProjResult<EEC::ProjArrayContainer>>> EECProjArrayTableProducer;

DEFINE_FWK_MODULE(EECProjUnbinnedTableProducer);
DEFINE_FWK_MODULE(EECProjVectorTableProducer);
DEFINE_FWK_MODULE(EECProjArrayTableProducer);


