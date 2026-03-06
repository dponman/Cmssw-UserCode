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

#include "SRothman/EECs/src/ProjTransferResult.h"

template <class ResultType>
class EECProjTransferTableProducer : public edm::stream::EDProducer<> {
public:
    explicit EECProjTransferTableProducer(const edm::ParameterSet&);
    ~EECProjTransferTableProducer() override = default;
    static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);
    void produce(edm::Event&, const edm::EventSetup&) override;
private:
    std::string name_;
    unsigned maxOrder_;

    edm::EDGetTokenT<std::vector<ResultType>> EECTransferToken_;
};

template <class ResultType>
EECProjTransferTableProducer<ResultType>::EECProjTransferTableProducer(const edm::ParameterSet& conf) :
        name_(conf.getParameter<std::string>("name")),
        maxOrder_(conf.getParameter<unsigned>("maxOrder")),
        EECTransferToken_(consumes<std::vector<ResultType>>(conf.getParameter<edm::InputTag>("EECTransfer"))) {

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
void EECProjTransferTableProducer<ResultType>::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    edm::ParameterSetDescription desc;

    desc.add<std::string>("name");
    desc.add<unsigned>("maxOrder", 6);
    desc.add<edm::InputTag>("EECTransfer");
    descriptions.addWithDefaultLabel(desc);
}

template <class ResultType>
void EECProjTransferTableProducer<ResultType>::produce(edm::Event& event, const edm::EventSetup& setup){
    edm::Handle<std::vector<ResultType>> EECTransfer_vec;
    event.getByToken(EECTransferToken_, EECTransfer_vec);

    if (!EECTransfer_vec->empty()) {
        const auto availableMaxOrder = EECTransfer_vec->front().result.get_data().size() + 1;
        if (maxOrder_ > availableMaxOrder) {
            throw cms::Exception("Configuration")
                << "Configured maxOrder=" << maxOrder_
                << " exceeds available result order " << availableMaxOrder;
        }
    }

    const unsigned nOrders = maxOrder_ - 1;

    std::vector<int> nR_reco;
    std::vector<int> nR_gen;

    std::vector<std::vector<int>> nEntries(nOrders);

    std::vector<int> iReco, iGen;
    std::vector<float> pt_denom_reco, pt_denom_gen;

    for (unsigned order=2; order<=maxOrder_; ++order){
        const unsigned orderIndex = order - 2;
        const std::string orderName = "Order" + std::to_string(order);
        std::vector<typename ResultType::T> transfered_R_reco;
        std::vector<typename ResultType::T> transfered_R_gen;
        std::vector<float> transfered_wt_reco, transfered_wt_gen;

        for (const auto& EEC : *EECTransfer_vec){
            const auto& data = EEC.result.get_data()[orderIndex];

            if (order == 2){
                nR_gen.push_back(data.nR_gen);
                nR_reco.push_back(data.nR_reco);

                iReco.push_back(EEC.iReco);
                iGen.push_back(EEC.iGen);

                pt_denom_reco.push_back(EEC.result.get_pt_denom_reco());
                pt_denom_gen.push_back(EEC.result.get_pt_denom_gen());
            }

            const auto& data_transfered = data.get_data();
                
            if constexpr (ResultType::IS_ARRAY){
                int entries = 0;
                for (unsigned iR_reco=0; iR_reco < data_transfered.shape()[0]; ++iR_reco){
                    for(unsigned iR_gen=0; iR_gen < data_transfered.shape()[3]; ++iR_gen){
                        double value = data_transfered[iR_reco][iR_gen];
                        if (value > 0){
                            entries++;
                            transfered_R_reco.push_back(iR_reco);
                            transfered_R_gen.push_back(iR_gen);
                            transfered_wt_reco.push_back(value);
                            transfered_wt_gen.push_back(value); //THIS IS WRONG
                                                                //BUT THE ARRAY DOES NOT SAVE THE GEN WEIGHT
                        }
                    }
                }
                if (entries == 0){
                    nEntries[orderIndex].push_back(1);
                    transfered_R_reco.push_back(-1);
                    transfered_R_gen.push_back(-1);
                    transfered_wt_reco.push_back(-1);
                    transfered_wt_gen.push_back(-1);
                } else {
                    nEntries[orderIndex].push_back(entries);
                }
            } else {
                if (data_transfered.size() > 0){
                    nEntries[orderIndex].push_back(data_transfered.size());
                    for (const auto& entry : data_transfered){
                        transfered_R_reco.push_back(entry.iR_reco);
                        transfered_R_gen.push_back(entry.iR_gen);
                        transfered_wt_reco.push_back(entry.wt_reco);
                        transfered_wt_gen.push_back(entry.wt_gen);
                    }
                } else {
                    nEntries[orderIndex].push_back(1);
                    transfered_R_reco.push_back(-1);
                    transfered_R_gen.push_back(-1);
                    transfered_wt_reco.push_back(-1);
                    transfered_wt_gen.push_back(-1);
                }
            }
        }

        auto dataTransferTable = std::make_unique<nanoaod::FlatTable>(transfered_wt_reco.size(), name_ + orderName, false);
        dataTransferTable->addColumn<typename ResultType::T>("R_reco", transfered_R_reco, "reco R index", ResultType::COLUMN_TYPE);
        dataTransferTable->template addColumn<typename ResultType::T>("R_gen", transfered_R_gen, "gen R index",    ResultType::COLUMN_TYPE);
        dataTransferTable->addColumn<float>("wt_reco", transfered_wt_reco, "weight", nanoaod::FlatTable::FloatColumn);
        dataTransferTable->addColumn<float>("wt_gen", transfered_wt_gen, "weight", nanoaod::FlatTable::FloatColumn);
        event.put(std::move(dataTransferTable), name_ + orderName);
    }

    auto BKTable = std::make_unique<nanoaod::FlatTable>(EECTransfer_vec->size(), name_+"BK", false);
    BKTable->template addColumn<int>("nR_reco", nR_reco, "nR reco",          nanoaod::FlatTable::IntColumn);
    BKTable->template addColumn<int>("nR_gen", nR_gen, "nR gen",             nanoaod::FlatTable::IntColumn);
    for (unsigned order=2; order<=maxOrder_; ++order){
        const unsigned orderIndex = order - 2;
        const std::string orderName = "Order" + std::to_string(order);
        BKTable->template addColumn<int>("nEntries" + orderName, nEntries[orderIndex], "nEntries", nanoaod::FlatTable::IntColumn);
    }
    BKTable->template addColumn<int>("iReco", iReco, "reco jet index",                            nanoaod::FlatTable::IntColumn);
    BKTable->template addColumn<int>("iGen", iGen, "gen jet index",                               nanoaod::FlatTable::IntColumn);
    BKTable->template addColumn<float>("pt_denom_reco", pt_denom_reco, "reco jet pt denominator", nanoaod::FlatTable::FloatColumn);
    BKTable->template addColumn<float>("pt_denom_gen", pt_denom_gen, "gen jet pt denominator",    nanoaod::FlatTable::FloatColumn);
    event.put(std::move(BKTable), name_+"BK");
}

typedef EECProjTransferTableProducer<EEC::CMSSWTransferResult<EEC::ProjTransferResult<EEC::ProjTransferVectorContainer<double>>>> EECProjTransferUnbinnedTableProducer;
typedef EECProjTransferTableProducer<EEC::CMSSWTransferResult<EEC::ProjTransferResult<EEC::ProjTransferVectorContainer<unsigned>>>> EECProjTransferVectorTableProducer;
typedef EECProjTransferTableProducer<EEC::CMSSWTransferResult<EEC::ProjTransferResult<EEC::ProjTransferArrayContainer>>> EECProjTransferArrayTableProducer;

DEFINE_FWK_MODULE(EECProjTransferUnbinnedTableProducer);
DEFINE_FWK_MODULE(EECProjTransferVectorTableProducer);
DEFINE_FWK_MODULE(EECProjTransferArrayTableProducer);


